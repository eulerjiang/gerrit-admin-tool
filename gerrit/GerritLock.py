'''
Created on 2012-5-21

@author: ejiawen
'''
import re
import os

class GerritAccessControlEditor(object):
    def __init__(self):
        self.projectConfigFileName = 'project.config'
        self.groupsFileName = 'groups'
        self.accessControlBlocks = []
        self.groupsLines = []
    
    def initAccessControlBlocks(self):
        blocks = []
        
        f = open(self.projectConfigFileName, 'r')
        try:
            endBlockFlag = -1 # -1: not start; 0: start block; 1, finish block
            
            block = ""
            while True:
                line = f.readline()
                if not line:
                    #print("===============================================")
                    #print(block)
                    blocks.append( block.rstrip('\n') )
                    break
                result = re.match(r'^\[', line)
                if result != None:
                    if endBlockFlag == -1:
                        endBlockFlag = 0
                    elif endBlockFlag == 0:
                        endBlockFlag = 1
                
                if endBlockFlag == 1:
                    #print("===============================================")
                    #print(block)
                    blocks.append( block.rstrip('\n') )
                    block = ""
                    endBlockFlag = 0
                block += line
        finally:
            f.close()
        self.accessControlBlocks = blocks
    
    def printContent(self):
        for oneBlock in self.accessControlBlocks:
            print(oneBlock)

    def updateAccessControlBlocks(self, updateRefsName, excludeGroupName, codeReviewMode = "YES"):
        index = 0
        
        if len(self.accessControlBlocks) == 0:
            print("init access control blocks")
            self.initAccessControlBlocks()
        
        isMatched = False
        for oneBlock in self.accessControlBlocks:
            result = re.match(".*access[ ]+\"" + updateRefsName + "\".*", oneBlock)
            if result != None:
                isMatched = True
                self.accessControlBlocks[index] = self._lockRefs(self.accessControlBlocks[index], updateRefsName, excludeGroupName, codeReviewMode)
            index += 1
            
        if isMatched == False:
            ## it need add access
            newAccessControlLine = '[access "' + updateRefsName + '"]'
            self.accessControlBlocks.append(self._lockRefs(newAccessControlLine, updateRefsName, excludeGroupName, codeReviewMode))
            
    def _lockRefs(self, oneAccessBlock, updateRefsName,excludeGroupName, codeReviewMode = "YES"):
        # Submit Lock
        newAccessBlock = ""
    
        accessControlLine = oneAccessBlock.split("\n")[0] + "\n"
        newAccessBlock += accessControlLine
    
        if codeReviewMode == "YES":
            accessGroupDefLines = "\tsubmit = group " + excludeGroupName + "\n"
        else:
            accessGroupDefLines = "\tpushMerge = group " + excludeGroupName + "\n"
        accessGroupDefLines += "\tpush = group " + excludeGroupName + "\n"
        
        newAccessBlock += accessGroupDefLines
        print("update access control for refs: " + updateRefsName)
        print("before:")
        print(oneAccessBlock)
        print("after:")
        print(newAccessBlock)
        
        return newAccessBlock

    def writeAcessControlFile(self):
        f = open(self.projectConfigFileName, 'w')
        try:
            for oneBlock in self.accessControlBlocks:
                f.write(oneBlock + "\n")
        finally:
            f.close()                  

    def writeGroupsFile(self, groupName, groupUUID):
        isNotInFile = True

        f = open(self.groupsFileName, 'r')
        try:
            while True:
                line = f.readline()
                if not line:
                    break
                self.groupsLines.append(line)
                if line.find(groupUUID) != -1:
                    isNotInFile = False
        finally:
            f.close()
        #
        if isNotInFile:    
            f = open(self.groupsFileName, 'w')
            try:
                for oneLine in self.groupsLines:
                    f.write(oneLine)
                f.write(groupUUID + "\t" + groupName + "\n")
            finally:
                f.close()  
        
    def pull(self):
        os.system( "git pull")

    def push(self, commitMessage = ""):
        commitMsg = "auto-update access control: "
        if commitMessage != "":
            commitMsg += commitMessage
        os.system( "git pull; git commit -am \"auto-update access control: " + commitMsg + "\"; git push origin HEAD:refs/meta/config")

def testGerritAccessControlEditor():
    gerritLock = GerritAccessControlEditor()
    #gerritLock.initAccessControlBlocks()
    gerritLock.updateAccessControlBlocks("refs/heads/ma63_fix_ep", "Administors", "YES")
        
if __name__ == '__main__':
    refsName = "refs/heads/ma63_fix_ep"
    excludeGroupName = "cbc/ma-master-lock"
    
    ## create group
    
    ## 
    gerritLock = GerritAccessControlEditor()
    gerritLock.pull()
    gerritLock.initAccessControlBlocks()
    gerritLock.updateAccessControlBlocks(refsName, excludeGroupName)
    gerritLock.writeAcessControlFile()
    gerritLock.push()
    
    # update group