import os
import sys
import pysvn
import time
import git

add_file_list = []
log_string = ''

def svn_update(path) :
    client = pysvn.Client()
    entry = client.info(path)
    updateResults = client.update(path)
    revNum = 0
    if updateResults :
        updateResult = updateResults[0]
        revNum = updateResult.number
    print('updated from ', entry.revision.number, ' to ', revNum)
    
    head = pysvn.Revision(pysvn.opt_revision_kind.number, entry.revision.number)
    end = pysvn.Revision(pysvn.opt_revision_kind.number, revNum)
    
    log_messages = client.log(path, revision_start=head, revision_end=end,limit=0)
    
    for log in log_messages :
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log.date))
        logstr = '[%s]\t%s\t%s\n  %s\n' % (log.revision.number, timestamp, log.author, log.message)
        print(logstr)
        global log_string
        log_string += logstr
        
    FILE_CHANGE_INFO = {
        pysvn.diff_summarize_kind.normal: ' ',
        pysvn.diff_summarize_kind.modified: 'M',
        pysvn.diff_summarize_kind.delete: 'D',
        pysvn.diff_summarize_kind.added: 'A',
    }    
    print('file changed: ')
    summary = client.diff_summarize(path, head, path, end)
    for info in summary :
        p = info.path
        if info.node_kind == pysvn.node_kind.dir :
            p += '/'
        file_changed = FILE_CHANGE_INFO[info.summarize_kind]
        prop_changed = ' '
        if info.prop_changed :
            prop_changed = 'M'
        print(file_changed + prop_changed, path)
        add_file_list.append(path)
    print("changed " + str(len(add_file_list)) + " file(s).")
    return revNum
        
def git_commit(path, msg) :
    global add_file_list
    if (len(add_file_list) > 0) :
        repo = git.Repo(path)
        for addedPath in add_file_list :
            repo.git.add(addedPath)
        print(repo.git.commit(m=msg))
   
def main() :
    path = "."
    revNum = svn_update(path)
    l = 'revision: %s \n\n' % (revNum)
    global log_string
    l += log_string
    git_commit(path, l)
    print("done.  ")
    os.system('Pause')
        
if __name__ == "__main__" :
    main()