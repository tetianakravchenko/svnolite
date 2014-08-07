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
	#url = "file://"+repo_home+"/svn-admin"
	os.chdir(work_dir)
        client.update(work_dir, recurse=True)
	rev = client.info(work_dir).get("revision").number	
#rev = pysvn.Revision( pysvn.opt_revision_kind.number, 2 )
	print "Current revision number: "+str(rev)
	if not check_if_modified(work_dir+"/keys/"):	##if exist modifications
		authorize_key_gen()		
	print check_if_modified(work_dir+"/conf/")	

def check_if_modified(filename):
	dict_status = {}
	for i in [f for f in os.listdir(filename) if not f.startswith('.')]:
		status = str( client.status(filename+i)[0].text_status)
		if status != 'normal':
			dict_status[filename+i] = status
	if dict_status:
		return True   #is empty
	else:	
		print dict_status
		return False   #is not empty
#return status in pysvn.wc_status_kind.added
#		print "Some files were added"
#    try:
#        s = client.status(filename)[0].text_status

#    catch pysvn.ClientError:
#        return False
#    else:
#        return s in (
#            pysvn.wc_status_kind.added, 
#            pysvn.wc_status_kind.deleted,
#            pysvn.wc_status_kind.replaced)
	###TODO: update, if exist changes: 1) in conf:
		## a) svnserve.conf: restart svnserve?
		## b) auth: 
	
	#if os.listdir(work_dir+"/keys"):
	#	authorize_key_gen() 

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
                authozile_file.write('command="svnserve -t -r {0} --config-file=/home/svn/svnserve.conf --tunnel-user{1}",no-port-forwarding,no-agent-forwarding,no-X11-forwarding,no-pty '.format(repo_home, i.split(".")[0]) + keys.read())
                keys.close()    

        authozile_file.close()

if not os.path.exists(repo_home+"/svn-admin"):
	create_svn_admin()
else:
	svn_admin_update()
#bin_work_dir_template()
