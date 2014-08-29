svnolite
========
### steps to install

First, prepare:

*   create new user "svn" with home directory "/home/svn"
*   install python-svn, git
*   login to "svn" on the server
*   make sure `~/.ssh/authorized_keys` not content information that you need (this file will be rewrited)

Next, install svnolite by running these commands:
    
    mkdir $HOME/svnolite-dir
    git clone git://github.com/ins0mia/svnolite
    cp -r $HOME/svnolite $HOME/svnolite-dir
    cd $HOME/svnolite-dir
    ./svnolite-installer.py

P.S. Afrer this step must be created: /home/svn/repositories/svn-admin; /home/svn/bin (with work copy); files: /home/svn/authz, /home/svn/svnserve.conf


## adding users and repos

#for adding new user:
add file with user`s key with name, ex. user.pub to directory svn-admin/keys

#for adding repo and giving permisions to users:
in file conf/authz add line in format [repo:/] ([repo:/path/to/some/dir])
and after this add permisions in format
user1 = rw
user2 = r

So we have:
[repo:/path/]
user1 = rw
user2 = r
