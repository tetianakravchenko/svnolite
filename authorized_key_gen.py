#!/usr/bin/python
import os

work_dir="/home/tanya/tmp/repo"
home_dir_ssh="/home/tanya/tmp/.ssh"

os.chdir(work_dir)

if os.path.exists(home_dir_ssh+"/authorized_keys"):
	open(home_dir_ssh+"/authorized_keys", 'w').close()
else:
	print "Sorry, but file authorized_keys is not found. This file will be created"
	open(home_dir_ssh+"/authorized_keys", 'a').close()

keys_list = [f for f in os.listdir(work_dir+"/keys")]
authozile_file = open (home_dir_ssh+"/authorized_keys", 'w+')

for i in keys_list:
	keys = open(work_dir+"/keys/"+i, 'r')
	authozile_file.write('command="svnserve -t -r /home/svn/repo --tunnel-user={0}",no-port-forwarding,no-agent-forwarding,no-X11-forwarding,no-pty '.format(i.split(".")[0]) + keys.read())
	keys.close()	

authozile_file.close()
