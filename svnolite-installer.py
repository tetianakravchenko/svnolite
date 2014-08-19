#!/usr/bin/python
import os, errno
import subprocess
import shutil
import pysvn
####ToDO: check if pysvn is installed

home_svn_dir="/home/svn"
home_svnolite_dir="/home/svn/svnolite"
work_dir="/home/svn/bin"
home_dir_ssh="/home/svn/.ssh"
repo_home="/home/svn/repositories"

client = pysvn.Client()
client.commit_info_style = 1

def dir_if_not_exist_create(directory):
	if not os.path.exists(directory):
               	os.makedirs(directory)

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
	#print "Revision is", output

def copy_configs(src, dst):
	for i in [f for f in os.listdir(src)]:
		shutil.copy(src+i, dst)	

def svn_admin_update():
	os.chdir(work_dir)
	current_rev_num_WC = client.info(work_dir).get("revision").number	
	print "WC revision number: "+str(current_rev_num_WC)
	#revision = pysvn.Revision(pysvn.opt_revision_kind.number, current_rev_num_WC)
	#print revision
	current_rev_num = client.revpropget("revision", "file:///home/svn/repositories/svn-admin")[0].number
	print "Current revision number: "+str(current_rev_num)
	if current_rev_num_WC < current_rev_num:
		print "Now will be executed 'svn update'"
		client.update(work_dir, recurse=True)
		if check_if_modified(current_rev_num):
			for i in check_if_modified(current_rev_num):
				if i.split('/')[1] == 'keys':
					authorize_key_gen()
				elif i.split('/')[1] == '/conf/svnserve.conf':
					
					##TODO
					print "'Conf' was changed"
				
	
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
        print  diff_paths
	if diff_paths == []:
		print "There is no changes"
		return False
	else:
		return diff_paths
				
	
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

def modified_conf_svnserve():
	svnserve_config = open(work_dir+"/conf/svnserve.con", 'r')
	###TODO
 
def modefied_auth():
	order_list = []
	for i in [re.findall('^[^#].+:.*$',line) for line in open(work_dir+"conf/auth")]:
		if i != []:
			order_list.append(i[0])
	print order_list
	for i in range(0, len(order_list)):
		order_list[i] = re.sub('["["]','', order_list[i]).split(":")[0] 
				
	order_list = lisr(set(order_list))
        for i in order_list:
		if testURL("file://"+repo_home+"/"+i):
			print "Repo " + i + "exist."
		else:
			print "Repository {0} don`t exist. {0} will be created".format(i)
			os.chdir(repo_home)
			p = subprocess.Popen("svnadmin create "+i, stdout=subprocess.PIPE, shell=True)
        		(output, err) = p.communicate() 
		

def testURL(url):
	try:
        	client.info2(url)
        	return True
	except pysvn.ClientError, ce:
        	if ('non-existant' in ce.args[0]) or ('Host not found' in ce.args[0]):
			print "Repo dont exist"
            		return False
        	else:
            		raise ce
###TODO: update, if exist changes: 1) in conf:
		## a) svnserve.conf: restart svnserve?
		## b) auth: 
	
##TODO: arg to input: in if i.split('/')[2].split('.')[0]
def authorize_key_gen():
	os.chdir(work_dir)
        if os.path.exists(home_dir_ssh+"/authorized_keys"):
                open(home_dir_ssh+"/authorized_keys", 'w').close()
        else:
                print "Sorry, but file authorized_keys is not found. This file will be created"
                open(home_dir_ssh+"/authorized_keys", 'a').close()

        keys_list = [f for f in os.listdir(work_dir+"/keys") if not f.startswith('.')]
        authozile_file = open (home_dir_ssh+"/authorized_keys", 'w+')

        for i in keys_list:
                keys = open(work_dir+"/keys/"+i, 'r')
                authozile_file.write('command="svnserve -t -r {0} --config-file=/home/svn/svnserve.conf --tunnel-user={1}",no-port-forwarding,no-agent-forwarding,no-X11-forwarding,no-pty '.format(repo_home, i.split(".")[0]) + keys.read())
                keys.close()    

        authozile_file.close()

if not os.path.exists(repo_home+"/svn-admin"):
	create_svn_admin()
else:
	svn_admin_update()
