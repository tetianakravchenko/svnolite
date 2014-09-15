#!/usr/bin/python
import os, errno, re
import subprocess
import shutil
import pysvn
import ConfigParser
import datetime 
import logging
import logging.handlers
import sys, getopt
####TODO: check if pysvn is installed
####TODO: set correct umask(750)		check
####TODO: post-commit - in svnolite.log		check
####TODO: change name to svnolite.py		+
###TODO: del path "home/svn" in 2 place		+
###TODO: create dir .ssh if not exist		+
###TODO: 3 mode: install + admin key + in authz give permisions; post-commit; reset admin key
###TODO: help (modes + link to github)
###TODO: fix adding keys after commit

home_svn_dir=str(os.path.split(os.getcwd())[0])
home_svnolite_dir=home_svn_dir+"/svnolite-dir"
work_dir=home_svn_dir+"/bin"
home_dir_ssh=home_svn_dir+"/.ssh"
repo_home=home_svn_dir+"/repositories"

# filesize in MB
log_file_rotate_size=10

client = pysvn.Client()
client.commit_info_style = 1

if not os.path.exists(home_svnolite_dir+'/svnolite.log'):
	open(home_svnolite_dir+'/svnolite.log', 'a').close()

#logging.basicConfig(filename=home_svnolite_dir+'/svnolite.log',level=logging.DEBUG)
logger = logging.getLogger('logger_for_svnolite.log')
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(filename=home_svnolite_dir+'/svnolite.log', maxBytes=log_file_rotate_size*1024, backupCount=5)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#handler.setFormatter(formatter)
logger.addHandler(handler)

def custimize_svn_admin():
	url = "file://"+repo_home+"/svn-admin"
        path = work_dir	
	if not os.path.exists(work_dir):
                client.checkout(url, path, recurse=True)
                dir_if_not_exist_create(work_dir+"/conf")
		dir_if_not_exist_create(work_dir+"/keys")
                copy_configs(home_svnolite_dir+"/template_conf/", work_dir+"/conf")
                client.add([work_dir+"/conf", work_dir+"/keys"], recurse = True)
                client.checkin([work_dir+"/conf", work_dir+"/keys"], "template_config", recurse = True)
	
def create_svn_admin():
	dir_if_not_exist_create(repo_home)
        os.chdir(repo_home)
        p = subprocess.Popen("svnadmin create svn-admin", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
	custimize_svn_admin()
	copy_configs(home_svnolite_dir+"/template_conf/", home_svn_dir+"/")
	logger.info(current_time()+" svn-admin repository created and customized")
	if not os.path.exists(repo_home+'/svn-admin/hooks/post-commit'):
		post_commit()
	#print "Revision is", output

def post_commit():
	with open(repo_home+'/svn-admin/hooks/post-commit','w+') as f:
		f.write('#!/bin/bash \n')
		f.write('logger -t [svnolite: ] -f ' + home_svnolite_dir+'/svnolite.log ' + '`python ' + os.path.realpath(__file__))
	os.chmod(repo_home+'/svn-admin/hooks/post-commit', 0755)

def current_time():
	return str(datetime.datetime.now())

def svn_admin_update():
	os.chdir(work_dir)
	current_rev_num_WC = client.info(work_dir).get("revision").number	
	logger.info("WC revision number: "+str(current_rev_num_WC))
	#revision = pysvn.Revision(pysvn.opt_revision_kind.number, current_rev_num_WC)
	#print revision
	current_rev_num = client.revpropget("revision", "file://"+repo_home+"/svn-admin")[0].number
	logger.info("Current revision number: "+str(current_rev_num))
	if current_rev_num_WC < current_rev_num:
		logger.info("Now will be executed 'svn update'")
		client.update(work_dir, recurse=True)
		logger.info(current_time()+" svn-admin repository was updated")
		if check_if_modified(current_rev_num):
			for i in check_if_modified(current_rev_num):
				if i.split('/')[1] == 'keys':
					authorize_key_gen()
				elif i.split('/')[2] == 'authz':
					modified_authz()	
					logger.info("'Authz' file was modified")
				elif i.split('/')[2] == 'svnserve.conf':
					logger.info("'svnserve.conf' was changed")
					modified_conf_svnserve()
				else:
					logger.info("Error: strange modification")
		else:
			logger.info("No changes there.")				
	
def check_if_modified(revision_number):	
	revision = pysvn.Revision(pysvn.opt_revision_kind.number, revision_number)
	#print str(revision)
	log = client.log(work_dir, discover_changed_paths=True, revision_end=revision)
	#print log
	diff_paths = []
	for i in log:
   		paths = i['changed_paths']
    		for j in paths:
      			if j['action'] in ['A', 'M', 'U', 'D']:
        			diff_paths.append(str(unicode(j['path'])))
        #print  diff_paths
	if diff_paths == []:
		logger.info("There is no changes")
		return False
	else:
		return diff_paths
				
	
def modified_conf_svnserve():
	os.chdir(work_dir+'/conf')
	valid_value = {'general': {'anon-access':'write|read|none',
                                'auth-access':'write|read|none',
                                'authz-db': 'authz|/.+/authz'}}
	try:   
        	parser = ConfigParser.SafeConfigParser()
        	parser.read(work_dir+"/conf/svnserve.conf")
	except ConfigParser.ParsingError, err:
                logger.error('Could not parse: ', err)

	if parser.sections() != valid_value.keys():
        	logger.warn("Name of section: [general] was changed or section was deleted")
	else:  
        	if parser.options('general') != valid_value['general'].keys():
                	logger.warn("You add/delete or modified standard options! Must be: 'anon-access', 'auth-access'and 'authz-db'")
        	else:  
                	for i in parser.options('general'):
                        	if not re.match(valid_value['general'][i],parser.get('general',i)):
                                	logger.error("Bad value in {0}. Accept values: 'anon-access':'write|read|none', 'auth-access':'write|read|none', 'authz-db': filename".format(i.upper()))
                	if not os.path.exists(parser.get('general','authz-db')):
                        	logger.warn("File {0} dont exist!".format(parser.get('general','authz-db')))
	shutil.copy(work_dir+"/conf/svnserve.conf", home_svn_dir)
 
def modified_authz():
	order_list = []
	for i in [re.findall('^[^#].+:.*$',line) for line in open(work_dir+"/conf/authz")]:
		if i != []:
			order_list.append(i[0])
	logger.info('Changes occured in file:', order_list)
	for i in range(0, len(order_list)):
		order_list[i] = re.sub('["["]','', order_list[i]).split(":")[0] 
				
	order_list = list(set(order_list))
        for i in order_list:
		if testURL("file://"+repo_home+"/"+i):
			logger.info("Repository " + i + " exist.")
		else:
			logger.info("Repository {0} don`t exist. {0} will be created".format(i))
			os.chdir(repo_home)
			p = subprocess.Popen("svnadmin create "+i, stdout=subprocess.PIPE, shell=True)
        		(output, err) = p.communicate() 
		
	shutil.copy(work_dir+"/conf/authz", home_svn_dir)	

def testURL(url):
	try:
        	client.info2(url)
        	return True
	except pysvn.ClientError, ce:
        	if ('Unable to open repository' in ce.args[0]) or ('Host not found' in ce.args[0]):
			#logging.info("Repo dont exist")
            		return False
        	else:
            		raise ce
	
##TODO: arg to input: in if i.split('/')[2].split('.')[0]
def authorize_key_gen():
	dir_if_not_exist_create(home_svn_dir+"/.ssh")
	os.chdir(work_dir)
        if os.path.exists(home_dir_ssh+"/authorized_keys"):
                open(home_dir_ssh+"/authorized_keys", 'w').close()
        else:
                logger.info("Sorry, but file authorized_keys is not found. This file will be created")
                open(home_dir_ssh+"/authorized_keys", 'a').close()

        keys_list = [f for f in os.listdir(work_dir+"/keys") if not f.startswith('.')]
        authozile_file = open (home_dir_ssh+"/authorized_keys", 'w+')

        for i in keys_list:
                keys = open(work_dir+"/keys/"+i, 'r')
                authozile_file.write('command="svnserve -t -r {0} --config-file=/home/svn/svnserve.conf --tunnel-user={1}",no-port-forwarding,no-agent-forwarding,no-X11-forwarding,no-pty '.format(repo_home, i.split(".")[0]) + keys.read())
                keys.close()    

        authozile_file.close()

def dir_if_not_exist_create(directory):
	if not os.path.exists(directory):
               	os.makedirs(directory, 0750)

def copy_configs(src, dst):
	for i in [f for f in os.listdir(src)]:
		shutil.copy(src+i, dst)	

# This function check if exist modification on local work copy before commit
#def check_if_modified(filename):
#	dict_status = {}
#	for i in [f for f in os.listdir(filename) if not f.startswith('.')]:
#		#status = str( client.status(filename+i)[0].text_status)
#		status = str( client.status(filename+i, recurse=True, update=False)[0].text_status)
#		if status != 'normal':
#			dict_status[filename+i] = status
#	if dict_status:
#		print dict_status
#		return True   #is empty
#	else:	
#		print dict_status
#		return False   #is not empty
#
#Bag 1: When commit, and in svnserve.conf is bad value!
#Bag 2: recreate log file! 
if not os.path.exists(repo_home+"/svn-admin"):
	create_svn_admin()
else:
	f_not_exist_createsvn_admin_update()
