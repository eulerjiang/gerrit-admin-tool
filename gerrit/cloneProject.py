'''
Created on 2012-5-29

@author: ejiawen
'''
import os

class cloneProject(object):
    def __init__(self, gerritServer, gerritProject, localRepoDir):
        self.gerritServer = gerritServer
        self.gerritProject = gerritProject
        
        self.gerritUrl = "ssh://" + gerritServer + ":29418/" + gerritProject
        self.localRepoName = localRepoDir
        
        self.refs = "refs/meta/config"
        self.branch = 'meta_config'
    
    def cloneRepo(self):
        cloneCommand = "git clone --no-checkout " + self.gerritUrl + " " + self.localRepoName
        os.system(cloneCommand)
        
        os.chdir(self.localRepoName)
        
        pullMetaRefsCommand = 'git pull ' + self.gerritUrl + ' '  + self.refs
        checkoutCommand = 'git checkout -b ' + self.branch + ' FETCH_HEAD'
        os.system(pullMetaRefsCommand)
        os.system(checkoutCommand)
    
    def pull(self):
        pullMetaRefsCommand = 'git pull ' + self.gerritUrl + ' '  + self.refs
        print(pullMetaRefsCommand)
        os.system(pullMetaRefsCommand)

    def showChange(self):
        os.system('git diff')
        print("")
                            
    def push(self, commitMessage = ""):
        commitMsg = "auto-update access control: "
        if commitMessage != "":
            commitMsg += commitMessage
            
        pushCommand = "git commit --no-verify -am \"auto-update access control: " + commitMsg + "\"; git push origin HEAD:refs/meta/config"
        print(pushCommand)
        os.system(pushCommand )
        print("")