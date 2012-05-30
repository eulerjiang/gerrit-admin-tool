gerrit-admin-tool
=================

Gerrit branch lock and group admin command line

Support 
* gerrit lock branch

* gerrit group member management: add user, remove user, reset group member.

---------------------
Required:

Python 2.7.3

Gerrit 2.2.1 or higher version

Gerrit Administrator Authority

---------------------
Usage:
Example: create group and lock branch 

  > python lockGerritBranch.py -gerrit-host <gerrit-server> -gerrit-project <projectName> -branch <refs/head/branch> -create <groupName> 
  
  > python lockGerritBranch -gerrit-host <gerrit-server> -gerrit-project <projectName> -branch <refs/head/branch> -create <groupName> <user1> <user2> ...

Example: update group members 

  > python lockGerritBranch -gerrit-host <gerrit-server> -add <groupName> <user1> <user2> ...
  
  > python lockGerritBranch -gerrit-host <gerrit-server> -remove <groupName> <user1> <user2> ...
  
  > python lockGerritBranch -gerrit-host <gerrit-server> -reset <groupName> <user1> <user2> ...
