'''
Created on 2012-5-28

@author: ejiawen
'''
import re
import subprocess

enableDebugInfo = 0
 
def printDebugInfo(message):
    if enableDebugInfo == 1:
        print(message)
    
class GroupAdmin(object):
    def __init__(self, gerritURL):
        self.gerritURL = gerritURL
        self.gerritCmdPrefix = "ssh -p 29418 " + gerritURL + " gerrit"
        
        self.account_external_ids_table = ""
        self.account_groups_table = ""
        self.account_group_members_table = ""
          
    def _testLogin(self):
        self.getGerritVersion()
        self.getDatabaseType()
        
    def executeCmd(self, cmd):
        printDebugInfo("===")
        print("=== Execute ")
        print(cmd)
        printDebugInfo("===")
        
        executeResult = subprocess.check_output(cmd, shell=True)

        printDebugInfo("=== Execute Result: " + executeResult)

        return executeResult
    
    def executeSQLCmd(self, gsqlCommandList, gsqlInputFileName = "sqlcommand.txt"):
        gSQLCmd = self.gerritCmdPrefix + " gsql" + " < " + gsqlInputFileName
    
        printDebugInfo("===")
        print("=== Execute ")
        print(gSQLCmd)
        printDebugInfo("===")
        self.generateSQLCommandFile(gsqlCommandList, gsqlInputFileName)

        executeResult = subprocess.check_output(gSQLCmd, shell=True)
        
        printDebugInfo("=== Execute Result: ")
        printDebugInfo(executeResult)
        
        return executeResult
        
    def createGroup(self, newGroupName):
        createGroupCmd = self.gerritCmdPrefix + " create-group " + newGroupName 
        
        try:
            self.executeCmd(createGroupCmd)
        except Exception as inst:
            print(type(inst))

    def _setGroupMemeber(self, groupId, accountId, flag):        
        if flag == "ADD":
            gsqlCommandList = ["insert into account_group_members values ('" + accountId + "','" + groupId + "')"]
        elif flag == "REMOVE":
            gsqlCommandList = ["delete from account_group_members where account_id = '" + accountId + "' and group_id = '" + groupId + "'"]
            
        self.executeSQLCmd(gsqlCommandList)

    def _setGroupMemeberList(self, groupId, accountIdList, flag):
        gsqlCommandList = []
        if flag == "ADD":
            for accountId in  accountIdList:
                gsqlCommandList.append("insert into account_group_members values ('" + accountId + "','" + groupId + "')")
        elif flag == "REMOVE":
            for accountId in  accountIdList:
                gsqlCommandList.append("delete from account_group_members where account_id = '" + accountId + "' and group_id = '" + groupId + "'")
            
        self.executeSQLCmd(gsqlCommandList)
                        
    def setGroupMemeber(self, groupName, userName, flag):
        # update table
        accountId = self.getAccountIdByUserName(userName)
        groupId = self.getGroupIdByGroupName(groupName)
        
        self._setGroupMemeber(groupId, accountId, flag)

    def _resetGroupMembers(self, groupId, accountIdList):
        gsqlCommandList = []
        gsqlCommandList.append("delete from account_group_members where group_id = '" + groupId + "'")
        for accountId in  accountIdList:
            gsqlCommandList.append("insert into account_group_members values ('" + accountId + "','" + groupId + "')")
            
        self.executeSQLCmd(gsqlCommandList)
    
    def resetGroupMembers(self, groupName, userNameList):
        accountIdList = []
        
        groupId = self.getGroupIdByGroupName(groupName)
        
        for userName in userNameList.split():
            accountIdList.append(self.getAccountIdByUserName(userName))
            
        self._resetGroupMembers(groupId, accountIdList)
                    
    def addGroupMembers(self, groupName, userNameList):
        for oneUser in userNameList.split():
            if self.isGroupMemeber(oneUser, groupName) != 1:
                print("add user " + oneUser + " to group " + groupName)
                self.setGroupMemeber(groupName, oneUser, "ADD")
            else:
                print("user " + oneUser + " is already a memeber of group " + groupName)

    def removeGroupMembers(self, groupName, userNameList):
        for oneUser in userNameList.split():
            if self.isGroupMemeber(oneUser, groupName) == 1:
                print("remove user " + oneUser + " from group " + groupName)
                self.setGroupMemeber(groupName, oneUser, "REMOVE")
            else:
                print("user " + oneUser + " is not a memeber of group " + groupName)
                
    def isGroupMemeber(self, userName, groupName):
        isMemeber = 1
        
        accountId = self.getAccountIdByUserName(userName)
        groupId = self.getGroupIdByGroupName(groupName)
        
        gsqlCommandList = ["select * from account_group_members where account_id = '" + accountId + "' and group_id = '" + groupId + "'"]       
        executeResult = self.executeSQLCmd(gsqlCommandList)

        searched = re.search("1 row;", executeResult, re.MULTILINE)
        if searched == None:
            isMemeber = 0
        
        if isMemeber == 1:
            print(userName + " is member of group " + groupName)
        else:
            print(userName + " is not member of group " + groupName)
            
        return isMemeber
                             
    def getGerritVersion(self):
        getVersionCmd = self.gerritCmdPrefix + " version"
        
        gerritVersion = ""
        
        commandResult = self.executeCmd(getVersionCmd)
        searched = re.search('(?<=gerrit version )\d.*', commandResult)
        if searched != None:
            gerritVersion = searched.group(0)
        print('my version is ' + gerritVersion)
        
        return gerritVersion
    
    def getDatabaseType(self):
        gsqlInputFileName = "versionInput.txt"
        
        databaseType = "PostgreSQL"
        sqlResult = self.executeSQLCmd("", gsqlInputFileName)
        searched = re.search('.*PostgreSQL.*', sqlResult, re.MULTILINE)
        if searched != None:
            databaseType = 'PostgreSQL'
        else:
            raise Exception("Un-support database type, till now it only support PostgreSQL")
            
        return databaseType
        
    def getAccountIdByUserName(self, userName):
        accountId = '1'
        
        gerritUsername = "username:" + userName
        gsqlCommandList = ["select * from account_external_ids where external_id = 'username:" + userName + "'"]
        
        sqlResult = self.executeSQLCmd(gsqlCommandList)
        for oneLine in sqlResult.splitlines():
            if oneLine.find(gerritUsername) != -1:
                accountId = oneLine.split('|')[0].strip()
                print(accountId)
                break
        
        if accountId == 1:
            raise Exception("No such user " + userName + " or failed to fetch accountId from database")
        
        return accountId

    def getGroupIdByGroupName(self, groupName):
        groupId = "1"
        gsqlCommandList = ["select * from account_groups where name = '" + groupName + "'"]
        
        sqlResult = self.executeSQLCmd(gsqlCommandList)
        for oneLine in sqlResult.splitlines():
            if oneLine.find(groupName) != -1:
                groupId = oneLine.split('|')[1].strip()
                print(groupId)
                break
        if groupId == 1:
            raise Exception("No such group " + groupName + " or failed to fetch groupId from database")
            
        return groupId

    def getGroupUUIdByGroupName(self, groupName):
        groupUUId = "1"
        gsqlCommandList = ["select * from account_groups where name = '" + groupName + "'"]
        
        sqlResult = self.executeSQLCmd(gsqlCommandList)
        for oneLine in sqlResult.splitlines():
            if oneLine.find(groupName) != -1:
                groupUUId = oneLine.split('|')[7].strip()
                print(groupUUId)
                break
        if groupUUId == 1:
            raise Exception("No such group " + groupName + " or failed to fetch groupId from database")
            
        return groupUUId
                    
    def generateSQLCommandFile(self, commandList, commandInputFileName = ""):
        f = open(commandInputFileName, 'w')
        try:
            oneCommand = ""
            print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            print("SQL Command:")
            for oneCommand in commandList:
                print(oneCommand + ";")
                f.write(oneCommand + ";\n")
            if oneCommand != '\q':
                print("\q")
                f.write(oneCommand + "\q\n")
        finally:
            f.close()
        
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    ### Not use below methods
    def initUserGroupTables(self):
        gsqlCommandList_accountId = ["select * from account_external_ids where external_id"]
        gsqlCommandList_groupId = ["select * from account_groups"]
        gsqlCommandList_groupmember = ["select * from account_group_members"]
        
        self.account_external_ids_table = self.executeSQLCmd(gsqlCommandList_accountId)
        self.account_groups_table = self.executeSQLCmd(gsqlCommandList_groupId)
        self.account_group_members_table = self.executeSQLCmd(gsqlCommandList_groupmember)
               
if __name__ == '__main__':
    oneAdmin = GroupAdmin("gerritserver")
    #oneAdmin._testLogin()
    
    #oneAdmin.initUserGroupTables()
    
    #oneAdmin.getGroupIdByGroupName('cbc/ma-users')
    #print("")
    #oneAdmin.getAccountIdByUserName('ejiawen')
    #oneAdmin.isGroupMemeber("ejiawen", "cbc/ma-users")
    #oneAdmin.isGroupMemeber("jenkins1", "cbc/ma-users")
    
    oneAdmin.createGroup("cbc/ma-master-lock")
    enableDebugInfo = 1
    oneAdmin.isGroupMemeber("jenkins1", "cbc/ma-master-lock")
    oneAdmin.resetGroupMembers("cbc/ma-master-lock", "jenkins1 ejiawen")
    oneAdmin.isGroupMemeber("jenkins1", "cbc/ma-master-lock")
