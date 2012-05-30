'''
Created on 2012-5-29

@author: ejiawen
'''
import sys
import os

from gerrit import GroupAdmin
from gerrit import GerritLock
from gerrit import cloneProject

def listToString(userNameList):
    userList = ""
    for oneUser in userNameList:
        userList = userList +  " " + oneUser
    
    userList = userList.strip()
    print("update user: " + userList) 
    return userList
   
def resetGroupMember(gerritServer,groupName,userNameList):  
    ## create group
    groupAdmin = GroupAdmin.GroupAdmin(gerritServer)
    groupAdmin.resetGroupMembers(groupName, listToString(userNameList))

def addGroupMember(gerritServer,groupName,userNameList):    
    ## create group
    groupAdmin = GroupAdmin.GroupAdmin(gerritServer)
    groupAdmin.addGroupMembers(groupName, listToString(userNameList))

def removeGroupMember(gerritServer,groupName,userNameList):    
    ## create group
    groupAdmin = GroupAdmin.GroupAdmin(gerritServer)
    groupAdmin.removeGroupMembers(groupName, listToString(userNameList)) 

def lockBranch(gerritServer, gerritProject, refsName, groupName, userNameList):
    ## create group
    groupAdmin = GroupAdmin.GroupAdmin(gerritServer)
    groupAdmin.createGroup(groupName)
    groupAdmin.addGroupMembers(groupName, listToString(userNameList))
    
    groupUUID = groupAdmin.getGroupUUIdByGroupName(groupName)
    
    ## clone meta configuration file
    localRepoDir = os.path.curdir + os.sep + "repo"
    localRepoDir = os.path.abspath(localRepoDir)
    
    os.chdir(localRepoDir)
    
    cloneRepo = cloneProject.cloneProject(gerritServer, gerritProject, localRepoDir)
    
    if os.path.exists(localRepoDir + os.sep + '.git'):
        cloneRepo.pull()
    else:
        cloneRepo.checkoutRepo()
    
    ## edit lock and push back
    gerritLock = GerritLock.GerritAccessControlEditor()
    gerritLock.updateAccessControlBlocks(refsName, groupName)
    gerritLock.printContent()
    gerritLock.writeAcessControlFile()
    gerritLock.writeGroupsFile(groupName, groupUUID)
    
    cloneRepo.showChange()
    cloneRepo.push()
                  
def usage():
    message = """Usage:
$0 -gerrit-host <gerrit-server> -gerrit-project <projectName> -branch <refs/head/branch> -create <groupName> 
$0 -gerrit-host <gerrit-server> -gerrit-project <projectName> -branch <refs/head/branch> -create <groupName> <user1> <user2> ...
$0 -gerrit-host <gerrit-server> -add <groupName> <user1> <user2> ...
$0 -gerrit-host <gerrit-server> -remove <groupName> <user1> <user2> ...
$0 -gerrit-host <gerrit-server> -reset <groupName> <user1> <user2> ...
"""
    print(message)
  
if __name__ == '__main__':
    gerritServer = "UNSET"
    gerritProject = "UNSET"
    gerritRefs = "UNSET"
    groupOpt = "UNSET"
    
    groupName = "UNSET"
    userNameList = []
    num = 1
    while num < len(sys.argv):
        if sys.argv[num] == '-gerrit-host':
            gerritServer = sys.argv[num+1]
            num = num + 1
        elif sys.argv[num] == '-gerrit-project':
            gerritProject = sys.argv[num+1]
            num = num + 1
        elif sys.argv[num] == '-branch':
            gerritRefs = sys.argv[num+1]
            num = num + 1
        elif sys.argv[num] == '-create':
            groupOpt = "CREATE"
        elif sys.argv[num] == '-add':
            groupOpt = "ADD"
        elif sys.argv[num] == '-remove':
            groupOpt = "REMOVE"
        elif sys.argv[num] == '-reset':
            groupOpt = "RESET"
        elif sys.argv[num] == '-help':
            usage()
            sys.exit(1) 
        else:
            groupName = sys.argv[num]
            userNameList = sys.argv[num+1:]
            break
        num = num + 1
    
    print("gerrit server: " + gerritServer)
    print("group Name: " + groupName)
    print("user name list: ")
    print(userNameList)
    print("group operate: " + groupOpt)
    
    if groupOpt == "RESET":
        resetGroupMember(gerritServer,groupName,userNameList)
    elif groupOpt == "ADD":
        addGroupMember(gerritServer,groupName,userNameList)
    elif groupOpt == "REMOVE":
        removeGroupMember(gerritServer,groupName,userNameList)
    elif groupOpt == "CREATE":
        lockBranch(gerritServer, gerritProject, gerritRefs, groupName, userNameList)