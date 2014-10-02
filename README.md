svnolite
========
### steps to install

First, prepare:

*   create new user "svn" with home directory "/home/svn"
*   install python-svn(for RHEL-based distributions - pysvn), git
*   login as user "svn" on the server

Next, install svnolite by running these commands:
    
    * git clone git://github.com/ins0mia/svnolite
    * cp -r $HOME/svnolite $HOME/svnolite-dir
    * cd $HOME/svnolite-dir
    * python $HOME/svnolite.py -i [-k </path/to/admin/key.pub>]

P.S. Attention!! It's important to use Full path here!
P.P.S. Afrer this step must be created: /home/svn/repositories/svn-admin; /home/svn/bin (with work copy); files: /home/svn/authz, /home/svn/svnserve.conf

svnolite usage:
python $HOME/svnolite.py [-i] [-u] [-k </full/path/to/admin/key>] [-h]:
	-i	install: create repositories/svn-admin; bin; files: authz, svnserve.conf
	-u	update (post-commit): check where exist modifications (in authz file, svnserve.conf or user's keys) and apply this changes
	-k	rewrite .ssh/authorized_keys and add admin key, give permitions to svn-admin repository on authz file

--adding users and repos

--for adding new user:
	add file with user`s key with name, ex. user.pub to directory svn-admin/keys

--for adding repo and giving permisions to users:
	in file conf/authz add line in format [repo:/] ([repo:/path/to/some/dir])
	and after this add permisions in format
	user1 = rw
	user2 = r

So we have:
[repo:/path/]
user1 = rw
user2 = r
