'''idea is to carry out the testing you were doing manually on 20160825'''

import orgFixLinks as OFL
import logging
import os
import shutil
import pudb

#TODO need to depersonalize this since already put it on github

def operate_on_fileA_w(filename,runDebugger=False,isDryRun=False,showLog=False,runWPauses=True):
    '''operate on file A wrapper'''
    # OFL.db1=OFL.set_up_database()
    if showLog and runWPauses:
        wait_on_user_input('pausing to allow you to read text on screen before file is operated on and log file displayed')
    return OFL.operate_on_fileA(filename=filename,runDebugger=runDebugger,isDryRun=isDryRun,showLog=showLog)

def wait_on_user_input(comment1='Now pausing to allow you to examine database with command line tool; examine files with emacs;  or otherwise look at what is happening'):
    print comment1
    prompt1='Enter c or a single space to continue with script\n'
    # with OFL.keyboardInputLock:  #this is not necessary since no spidering in this script?
    resp=raw_input(prompt1)
    while (resp != "c") and (resp != " "):
        resp=raw_input(prompt1)

#head functions to test repair of links to org file
def test01(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''
    fileA links to fileB
    fileB is an org file
    move fileB while keeping its basename the same
    fileB never contains a unique ID'''

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    filenameA='20160817TestFile.org'
    filenameB='20160817TestFileLinkTarget.org'
    filenameAOrig='20160817TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160817TestFileLinkTarget.org.original'
    databaseName='orgFiles.sqlite'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is an org file','fileA and fileB start out without unique IDs','fileA gets a unique ID','fileB does not get a unique ID']
    blurbList.extend(['fileB is moved to another folder','basename of fileB is kept the same','an attempt is made to repair broken link to fileB in fileA'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToOrgFilesList)==1, 'fileA does not have a single link to an org file'
    assert fileA.linksToOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################
    
    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move fileB but keep basename the same
    os.rename(filenameB,os.path.join(anotherFolder,filenameB))
    print 'Just Moved fileB %s to folder %s while keeping basenameB the same' % (filenameB,anotherFolder)

    #####################################################

    print 'Now analyzing fileA %s a second time after moving fileB without changing basenameB; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
        testPasses=True
    else:
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    expectedRepairMethod='attemptRepairViaBasenameMatchOnDisk'
    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(os.path.join(anotherFolder,filenameB))
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test02(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''
    fileA links to fileB
    fileB is an org file
    insert a unique ID in fileB
    move fileB while keeping its basename the same
    '''

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160817TestFile.org'
    filenameB='20160817TestFileLinkTarget.org'
    filenameAOrig='20160817TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160817TestFileLinkTarget.org.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is an org file','fileA and fileB start out without unique IDs','fileA gets a unique ID','fileB gets a unique ID']
    blurbList.extend(['fileB is moved to another folder','basename of fileB is kept the same','an attempt is made to repair broken link to fileB in fileA'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToOrgFilesList)==1, 'fileA does not have a single link to an org file'
    assert fileA.linksToOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Now analyzing fileB %s; unique ID will be inserted' % filenameB
    
    showLog1=True
    fileB=operate_on_fileA_w(filenameB,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move fileB but keep basename the same
    os.rename(filenameB,os.path.join(anotherFolder,filenameB))
    print 'Just Moved fileB %s to folder %s while keeping basenameB the same' % (filenameB,anotherFolder)

    #####################################################

    print 'Now analyzing fileA %s a second time after moving fileB without changing basenameB; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
        testPasses=True
    else:
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    expectedRepairMethod='attemptRepairViaUniqueIDFromDatabaseAndBashFind'
    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(os.path.join(anotherFolder,filenameB))
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test03(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''
    fileA links to fileB
    fileB is an org file
    insert a unique ID in fileB
    fileA gets a unique ID in header for fileB
    move fileB while keeping its basename the same
    '''

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160817TestFile.org'
    filenameB='20160817TestFileLinkTarget.org'
    filenameAOrig='20160817TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160817TestFileLinkTarget.org.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    testPasses=True

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is an org file','fileA and fileB start out without unique IDs','fileA gets a unique ID','fileB gets a unique ID']
    blurbList.extend(['fileA gets uniqueID in header for fileB','fileB is moved to another folder','basename of fileB is kept the same','an attempt is made to repair broken link to fileB in fileA'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToOrgFilesList)==1, 'fileA does not have a single link to an org file'
    assert fileA.linksToOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Now analyzing fileB %s; unique ID will be inserted' % filenameB
    
    showLog1=True
    fileB=operate_on_fileA_w(filenameB,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    print 'Now analyzing fileA %s again; unique ID will be inserted in header for link to fileB' % filenameA
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    print 'Now analyzing fileA %s again; unique ID in header should now make it to fileA variable' % filenameA
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if not fileA.linksToOrgFilesList[0].targetObj.uniqueIDFromHeader==fileB.uniqueID:
        print 'unique ID in header of fileA for link to fileB does not match unique ID inside fileB; test fails'
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move fileB but keep basename the same
    os.rename(filenameB,os.path.join(anotherFolder,filenameB))
    print 'Just Moved fileB %s to folder %s while keeping basenameB the same' % (filenameB,anotherFolder)

    #####################################################

    print 'Now analyzing fileA %s after moving fileB without changing basenameB; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
    else:
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    # expectedRepairMethod='attemptRepairViaExpectedUniqueIDAndBashFind'
    expectedRepairMethod='attemptRepairViaUniqueIDFromHeaderAndBashFind'
    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(os.path.join(anotherFolder,filenameB))
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test04(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''fileB is an org file
    move fileB but keep its basename the same
    a unique ID is inserted in fileB prior to moving it
    fileA does not get a unique ID in header for fileB
    delete database before attempting repair
    this should be a test of ability of script to repair a link assuming basename is unchanged
    '''

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160817TestFile.org'
    filenameB='20160817TestFileLinkTarget.org'
    filenameAOrig='20160817TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160817TestFileLinkTarget.org.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    testPasses=True

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is an org file','fileA and fileB start out without unique IDs','fileA gets a unique ID','fileB gets a unique ID']
    blurbList.extend(['fileA does not get uniqueID in header for fileB','fileB is moved to another folder','basename of fileB is kept the same'])
    blurbList.extend(['database is deleted before attempting to repair broken link in fileA'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToOrgFilesList)==1, 'fileA does not have a single link to an org file'
    assert fileA.linksToOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Now analyzing fileB %s; unique ID will be inserted' % filenameB
    
    showLog1=True
    fileB=operate_on_fileA_w(filenameB,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    # print 'Now analyzing fileA %s again; unique ID will be inserted in header for link to fileB' % filenameA
    # showLog1=True
    # fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # if runWithPauses and (not showLog1):
    #     wait_on_user_input()

    #####################################################

    # print 'Now analyzing fileA %s again; unique ID in header should now make it to fileA variable' % filenameA
    # showLog1=True
    # fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # if not fileA.linksToOrgFilesList[0].targetObj.uniqueIDFromHeader==fileB.uniqueID:
    #     print 'unique ID in header of fileA for link to fileB does not match unique ID inside fileB; test fails'
    #     testPasses=False

    # if runWithPauses and (not showLog1):
    #     wait_on_user_input()

    #####################################################

    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move fileB but keep basename the same
    os.rename(filenameB,os.path.join(anotherFolder,filenameB))
    print 'Just Moved fileB %s to folder %s while keeping basenameB the same' % (filenameB,anotherFolder)

    #####################################################

    os.remove(databaseName)
    print 'Just deleted database'

    #####################################################

    print 'Now analyzing fileA %s after moving fileB without changing basenameB; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
    else:
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    # expectedRepairMethod='attemptRepairViaExpectedUniqueIDAndBashFind'
    # expectedRepairMethod='attemptRepairViaUniqueIDFromHeaderAndBashFind'
    expectedRepairMethod='attemptRepairViaBasenameMatchOnDisk'
    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(os.path.join(anotherFolder,filenameB))
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test05(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''fileB is an org file
    move fileB but keep its basename the same
    a unique ID is inserted in fileB prior to moving it
    fileA gets a unique ID in header for fileB
    delete database before attempting repair
    '''

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160817TestFile.org'
    filenameB='20160817TestFileLinkTarget.org'
    filenameAOrig='20160817TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160817TestFileLinkTarget.org.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    testPasses=True

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is an org file','fileA and fileB start out without unique IDs','fileA gets a unique ID','fileB gets a unique ID']
    blurbList.extend(['fileA gets a uniqueID in header for fileB','fileB is moved to another folder','basename of fileB is kept the same'])
    blurbList.extend(['database is deleted before attempting to repair broken link in fileA'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToOrgFilesList)==1, 'fileA does not have a single link to an org file'
    assert fileA.linksToOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Now analyzing fileB %s; unique ID will be inserted' % filenameB
    
    showLog1=True
    fileB=operate_on_fileA_w(filenameB,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    print 'Now analyzing fileA %s again; unique ID will be inserted in header for link to fileB' % filenameA
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    # print 'Now analyzing fileA %s again; unique ID in header should now make it to fileA variable' % filenameA
    # showLog1=True
    # fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # if not fileA.linksToOrgFilesList[0].targetObj.uniqueIDFromHeader==fileB.uniqueID:
    #     print 'unique ID in header of fileA for link to fileB does not match unique ID inside fileB; test fails'
    #     testPasses=False

    # if runWithPauses and (not showLog1):
    #     wait_on_user_input()

    #####################################################

    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move fileB but keep basename the same
    os.rename(filenameB,os.path.join(anotherFolder,filenameB))
    print 'Just Moved fileB %s to folder %s while keeping basenameB the same' % (filenameB,anotherFolder)

    #####################################################

    os.remove(databaseName)
    print 'Just deleted database'

    #####################################################

    print 'Now analyzing fileA %s after moving fileB without changing basenameB; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
    else:
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    # expectedRepairMethod='attemptRepairViaExpectedUniqueIDAndBashFind'
    expectedRepairMethod='attemptRepairViaUniqueIDFromHeaderAndBashFind'
    # expectedRepairMethod='attemptRepairViaBasenameMatchOnDisk'
    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(os.path.join(anotherFolder,filenameB))
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test06(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''fileB is an org file without a unique ID
    move fileB and change its basename
    repair should not be possible in this case
    '''

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160817TestFile.org'
    filenameB='20160817TestFileLinkTarget.org'
    filenameAOrig='20160817TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160817TestFileLinkTarget.org.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    testPasses=True

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is an org file','fileA and fileB start out without unique IDs','fileA gets a unique ID','fileB does not get a unique ID']
    blurbList.extend(['fileB is moved to another folder','basename of fileB is changed'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToOrgFilesList)==1, 'fileA does not have a single link to an org file'
    assert fileA.linksToOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    # print 'Now analyzing fileB %s; unique ID will be inserted' % filenameB
    
    # showLog1=True
    # fileB=operate_on_fileA_w(filenameB,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # if runWithPauses and (not showLog1):
    #     wait_on_user_input()

    #####################################################

    # print 'Now analyzing fileA %s again; unique ID will be inserted in header for link to fileB' % filenameA
    # showLog1=True
    # fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # if runWithPauses and (not showLog1):
    #     wait_on_user_input()

    #####################################################

    # print 'Now analyzing fileA %s again; unique ID in header should now make it to fileA variable' % filenameA
    # showLog1=True
    # fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # if not fileA.linksToOrgFilesList[0].targetObj.uniqueIDFromHeader==fileB.uniqueID:
    #     print 'unique ID in header of fileA for link to fileB does not match unique ID inside fileB; test fails'
    #     testPasses=False

    # if runWithPauses and (not showLog1):
    #     wait_on_user_input()

    #####################################################

    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move fileB but keep basename the same
    # os.rename(filenameB,os.path.join(anotherFolder,filenameB))
    #move fileB and change basename
    newNameB=os.path.join(anotherFolder,'NoName.org')
    os.rename(filenameB,newNameB)
    print 'Just moved fileB %s to %s' % (filenameB,newNameB)

    #####################################################

    print 'Now analyzing fileA %s after moving fileB; look for failed repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully; test failed'
        testPasses=False
    else:
        print 'Link in fileA to fileB is still broken; test passes'

    # expectedRepairMethod='attemptRepairViaExpectedUniqueIDAndBashFind'
    # expectedRepairMethod='attemptRepairViaUniqueIDFromHeaderAndBashFind'
    # expectedRepairMethod='attemptRepairViaBasenameMatchOnDisk'
    expectedRepairMethod=None
    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(newNameB)
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test07(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''fileB is an org file
    move and rename fileB; insert a unique ID in fileB prior to moving it'''

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160817TestFile.org'
    filenameB='20160817TestFileLinkTarget.org'
    filenameAOrig='20160817TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160817TestFileLinkTarget.org.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is an org file','fileA and fileB start out without unique IDs','fileA gets a unique ID','fileB gets a unique ID']
    blurbList.extend(['fileB is moved to another folder','basename of fileB is changed'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToOrgFilesList)==1, 'fileA does not have a single link to an org file'
    assert fileA.linksToOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Now analyzing fileB %s; unique ID will be inserted' % filenameB
    
    showLog1=True
    fileB=operate_on_fileA_w(filenameB,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move and rename fileB
    newNameB=os.path.join(anotherFolder,'NoName.org')
    os.rename(filenameB,newNameB)
    print 'Just moved fileB %s to %s' % (filenameB,newNameB)

    #####################################################

    print 'Now analyzing fileA %s a second time after moving fileB without changing basenameB; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
        testPasses=True
    else:
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    expectedRepairMethod='attemptRepairByLookingInsideFilesForUniqueID'
    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################
    
    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(newNameB)
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test08(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''fileB is an org file
    insert uniqueID in fileB
    fileA gets unique ID in header for link to fileB
    move and rename fileB
    repair broken link in fileA to fileB
    '''

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160817TestFile.org'
    filenameB='20160817TestFileLinkTarget.org'
    filenameAOrig='20160817TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160817TestFileLinkTarget.org.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is an org file','fileA and fileB start out without unique IDs','fileA gets a unique ID','fileB gets a unique ID']
    blurbList.extend(['fileA gets unique ID in header for link to fileB','fileB is moved to another folder','basename of fileB is changed'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToOrgFilesList)==1, 'fileA does not have a single link to an org file'
    assert fileA.linksToOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Now analyzing fileB %s; unique ID will be inserted' % filenameB
    
    showLog1=True
    fileB=operate_on_fileA_w(filenameB,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    print 'Now analyzing fileA %s again; unique ID will be inserted in header for link to fileB' % filenameA
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    print 'Now analyzing fileA %s again; unique ID in header should now make it to fileA variable' % filenameA
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if not fileA.linksToOrgFilesList[0].targetObj.uniqueIDFromHeader==fileB.uniqueID:
        print 'unique ID in header of fileA for link to fileB does not match unique ID inside fileB; test fails'
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move and rename fileB
    newNameB=os.path.join(anotherFolder,'NoName.org')
    os.rename(filenameB,newNameB)
    print 'Just moved fileB %s to %s' % (filenameB,newNameB)

    #####################################################

    print 'Now analyzing fileA %s again; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
        testPasses=True
    else:
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    expectedRepairMethod='attemptRepairByLookingInsideFilesForUniqueID'
    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################
    
    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(newNameB)
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test09(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''fileB is an org file
    insert a unique ID in fileB
    move and rename fileB
    delete database
    attempt repair of broken link to fileB
    '''

    testPasses=True

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160817TestFile.org'
    filenameB='20160817TestFileLinkTarget.org'
    filenameAOrig='20160817TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160817TestFileLinkTarget.org.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is an org file','fileA and fileB start out without unique IDs','fileA gets a unique ID','fileB gets a unique ID']
    blurbList.extend(['fileB is moved to another folder','basename of fileB is changed'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToOrgFilesList)==1, 'fileA does not have a single link to an org file'
    assert fileA.linksToOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Now analyzing fileB %s; unique ID will be inserted' % filenameB
    
    showLog1=True
    fileB=operate_on_fileA_w(filenameB,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move and rename fileB
    newNameB=os.path.join(anotherFolder,'NoName.org')
    os.rename(filenameB,newNameB)
    print 'Just moved fileB %s to %s' % (filenameB,newNameB)

    #####################################################

    os.remove(databaseName)
    print 'Just deleted database'

    #####################################################

    print 'Now analyzing fileA %s again; look for failed repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully; test failed'
        testPasses=False
    else:
        print 'Link in fileA to fileB is still broken; test passes'

    expectedRepairMethod=None
    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################
    
    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(newNameB)
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test10(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''fileB is an org file
    insert a unique ID in fileB
    fileA gets unique ID in header for link to fileB
    move and rename fileB
    delete database
    attempt repair of broken link to fileB
    '''

    testPasses=True

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160817TestFile.org'
    filenameB='20160817TestFileLinkTarget.org'
    filenameAOrig='20160817TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160817TestFileLinkTarget.org.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is an org file','fileA and fileB start out without unique IDs','fileA gets a unique ID','fileB gets a unique ID']
    blurbList.extend(['fileA gets unique ID in header for link to fileB','fileB is moved to another folder','basename of fileB is changed'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToOrgFilesList)==1, 'fileA does not have a single link to an org file'
    assert fileA.linksToOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Now analyzing fileB %s; unique ID will be inserted' % filenameB
    
    showLog1=True
    fileB=operate_on_fileA_w(filenameB,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    print 'Now analyzing fileA %s again; unique ID will be inserted in header for link to fileB' % filenameA
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    print 'Now analyzing fileA %s again; unique ID in header should now make it to fileA variable' % filenameA
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if not fileA.linksToOrgFilesList[0].targetObj.uniqueIDFromHeader==fileB.uniqueID:
        print 'unique ID in header of fileA for link to fileB does not match unique ID inside fileB; test fails'
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move and rename fileB
    newNameB=os.path.join(anotherFolder,'NoName.org')
    os.rename(filenameB,newNameB)
    print 'Just moved fileB %s to %s' % (filenameB,newNameB)

    #####################################################

    os.remove(databaseName)
    print 'Just deleted database'

    #####################################################

    print 'Now analyzing fileA %s again; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully; test passes'
    else:
        print 'Link in fileA to fileB is still broken; test fails'
        testPasses=False

    expectedRepairMethod='attemptRepairByLookingInsideFilesForUniqueID'

    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################
    
    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(newNameB)
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test11(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''fileB is an org file
    insert a unique ID in fileB
    move and rename fileB
    carry out repair of broken link in fileA
    edit fileA to have a link to old fileB
    repair will test the capability of using previous filename in database
    '''

    testPasses=True

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160817TestFile.org'
    filenameB='20160817TestFileLinkTarget.org'
    filenameAOrig='20160817TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160817TestFileLinkTarget.org.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is an org file','fileA and fileB start out without unique IDs','fileA gets a unique ID','fileB gets a unique ID']
    blurbList.extend(['fileB is moved to another folder','basename of fileB is changed','repair of broken link to fileB in fileA is done'])
    blurbList.extend(['fileA is edited so that repaired link to fileB is back to the original value','repair of this broken link tests previous filename repair capability'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToOrgFilesList)==1, 'fileA does not have a single link to an org file'
    assert fileA.linksToOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Now analyzing fileB %s; unique ID will be inserted' % filenameB
    
    showLog1=True
    fileB=operate_on_fileA_w(filenameB,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move and rename fileB
    newNameB=os.path.join(anotherFolder,'NoName.org')
    os.rename(filenameB,newNameB)
    print 'Just moved fileB %s to %s' % (filenameB,newNameB)

    #####################################################

    print 'Now analyzing fileA %s again; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
    else:
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    expectedRepairMethod='attemptRepairByLookingInsideFilesForUniqueID'
    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################
    #wish to change fileA such that link points to old fileB
    #cannot simply do this since there will be a unique ID mismatch and script will quit:
    # shutil.copy2(filenameAOrig,filenameA)
    # print 'Just replaced fileA with original fileA; link now points to old name of fileB'
    #must generate test file from current fileA so that unique ID matches the one in current fileA

    inp=file(filenameA,'r')
    oldLines2=[a for a in inp.readlines() if a.strip()]  #gets rid of lines that are just a newline \n character
    oldLines2[-1]=oldLines2[-1].replace(newNameB,filenameB)  #change the one outward link in filenameA to point to previous name of filenameB
    #20160901: oops: script had given link a description that matches new name; does not seem worth the trouble to erase this description
    inp.close()
    out=file(filenameA,'w')
    out.writelines(oldLines2)
    out.close()

    print 'Just rewrote fileA so that link points to previous name of fileB'

    #####################################################

    print 'Now analyzing fileA %s again; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
    else:
        #actually you have not checked if link is working or not
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    expectedRepairMethod='attemptRepairUsingTablePreviousFilenames'
    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################
    
    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(newNameB)
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test12(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''
    fileA initially contains a symlink that points to fileB
    fileB is an org file
    insert a unique ID in fileB
    move and rename fileB
    repair resulting broken link in fileA
    edit fileA to have a link to symlink that used to point to fileB
    use operating system commands to rename that symlink on disk with a different name, so script can't find it
    this tests repair of a broken link via symlinks table in database
    '''

    testPasses=True

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160817TestFile.org'
    filenameB='20160817TestFileLinkTarget.org'
    filenameAOrig='20160817TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160817TestFileLinkTarget.org.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is an org file','fileA and fileB start out without unique IDs','fileA gets a unique ID','fileB gets a unique ID']
    blurbList.extend(['fileB is moved to another folder','basename of fileB is changed','resulting broken link to fileB in fileA is repaired'])
    blurbList.extend(['fileA is edited so that repaired link to fileB is reverted to the original value of a symlink','repair of this broken link tests symlinks table repair method'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToOrgFilesList)==1, 'fileA does not have a single link to an org file'
    assert fileA.linksToOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Now analyzing fileB %s; unique ID will be inserted' % filenameB
    
    showLog1=True
    fileB=operate_on_fileA_w(filenameB,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move and rename fileB
    newNameB=os.path.join(anotherFolder,'NoName.org')
    os.rename(filenameB,newNameB)
    print 'Just moved fileB %s to %s' % (filenameB,newNameB)

    #####################################################

    print 'Now analyzing fileA %s again; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
    else:
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    expectedRepairMethod='attemptRepairByLookingInsideFilesForUniqueID'
    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################
    #change fileA such that link points to symlink to old fileB

    symlinkB='symlinkTo'+filenameB

    # this will not detect if symlinkB is gone from disk, because broken symlink fails os.path.exists
    # assert os.path.exists(symlinkB), 'Symlink %s is missing; cannot proceed with Test 12' % symlinkB
    assert os.path.islink(symlinkB), 'Symlink %s is missing; cannot proceed with Test 12' % symlinkB

    inp=file(filenameA,'r')
    oldLines2=[a for a in inp.readlines() if a.strip()]  #gets rid of lines that are just a newline \n character
    oldLines2[-1]=oldLines2[-1].replace(newNameB,symlinkB)  #change the one outward link in filenameA to point to previous symlink to fileB
    #20160901: oops: script had given link a description that matches new name; does not seem worth the trouble to erase this description
    inp.close()
    out=file(filenameA,'w')
    out.writelines(oldLines2)
    out.close()

    print 'Just rewrote fileA so that link points to symlink that pointed to previous fileB'

    #must do this or else script will convert symlink into what it points to, which would prevent repair by symlinks table
    tempSymlinkB=symlinkB+'.temp'
    os.rename(symlinkB,tempSymlinkB)
    #####################################################

    print 'Now analyzing fileA %s again; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    if fileA.linksToOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
    else:
        #actually you have not checked if link is working or not
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    expectedRepairMethod='attemptRepairUsingSymlinksTable'
    repairMethod=fileA.linksToOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################
    
    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(newNameB)
    os.remove(databaseName)
    os.rename(tempSymlinkB,symlinkB)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

#head functions to test repair of links to non org file
def test01B(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''
    fileA links to fileB
    fileB is an non org file
    move fileB while keeping its basename the same
    '''

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160825TestFile.org'
    filenameB='20160825TestFileLinkTarget.txt'
    filenameAOrig='20160825TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160825TestFileLinkTarget.txt.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is a non org file']
    blurbList.extend(['fileB is moved to another folder','basename of fileB is kept the same','an attempt is made to repair broken link to fileB in fileA'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToNonOrgFilesList)==1, 'fileA does not have a single link to a non org file'
    assert fileA.linksToNonOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################
    
    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move fileB but keep basename the same
    os.rename(filenameB,os.path.join(anotherFolder,filenameB))
    print 'Just Moved fileB %s to folder %s while keeping basenameB the same' % (filenameB,anotherFolder)

    #####################################################

    print 'Now analyzing fileA %s a second time after moving fileB without changing basenameB; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToNonOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
        testPasses=True
    else:
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    expectedRepairMethod='attemptRepairViaBasenameMatchOnDisk'
    repairMethod=fileA.linksToNonOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(os.path.join(anotherFolder,filenameB))
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test02B(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''
    fileA links to fileB
    fileB is an non org file
    move fileB while keeping its basename the same
    delete database before repair attempt
    '''

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160825TestFile.org'
    filenameB='20160825TestFileLinkTarget.txt'
    filenameAOrig='20160825TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160825TestFileLinkTarget.txt.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is a non org file']
    blurbList.extend(['fileB is moved to another folder','basename of fileB is kept the same','delete database','an attempt is made to repair broken link to fileB in fileA'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToNonOrgFilesList)==1, 'fileA does not have a single link to a non org file'
    assert fileA.linksToNonOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################
    
    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move fileB but keep basename the same
    os.rename(filenameB,os.path.join(anotherFolder,filenameB))
    print 'Just Moved fileB %s to folder %s while keeping basenameB the same' % (filenameB,anotherFolder)

    #####################################################

    os.remove(databaseName)
    print 'Just deleted database'

    #####################################################

    print 'Now analyzing fileA %s a second time after moving fileB without changing basenameB; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToNonOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
        testPasses=True
    else:
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    expectedRepairMethod='attemptRepairViaBasenameMatchOnDisk'
    repairMethod=fileA.linksToNonOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(os.path.join(anotherFolder,filenameB))
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test03B(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''fileB is a non org file
    move fileB and change its basename
    repair should not be possible in this case
    '''

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160825TestFile.org'
    filenameB='20160825TestFileLinkTarget.txt'
    filenameAOrig='20160825TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160825TestFileLinkTarget.txt.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    testPasses=True

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileB is a non org file']
    blurbList.extend(['fileB is moved to another folder','basename of fileB is changed','repair should not be possible'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToNonOrgFilesList)==1, 'fileA does not have a single link to an org file'
    assert fileA.linksToNonOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################

    origFolder=os.path.split(fileA.filenameAP)[0]
    
    #move fileB but keep basename the same
    # os.rename(filenameB,os.path.join(anotherFolder,filenameB))
    #move fileB and change basename
    newNameB=os.path.join(anotherFolder,'NoName.txt')
    os.rename(filenameB,newNameB)
    print 'Just moved fileB %s to %s' % (filenameB,newNameB)

    #####################################################

    print 'Now analyzing fileA %s after moving fileB; look for failed repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToNonOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToNonOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully; test failed'
        testPasses=False
    else:
        print 'Link in fileA to fileB is still broken; test passes'

    # expectedRepairMethod='attemptRepairViaExpectedUniqueIDAndBashFind'
    # expectedRepairMethod='attemptRepairViaUniqueIDFromHeaderAndBashFind'
    # expectedRepairMethod='attemptRepairViaBasenameMatchOnDisk'
    expectedRepairMethod=None
    repairMethod=fileA.linksToNonOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(newNameB)
    os.remove(databaseName)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

def test04B(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    return None
#     '''fileB is a non org file
#     move and rename fileB
#     carry out repair of broken link in fileA
#     edit fileA to have a link to old fileB
#     repair will test the capability of using previous filename in database
#     '''

#     testPasses=True

#     databaseName='orgFiles.sqlite'
#     filenameA='20160825TestFile.org'
#     filenameB='20160825TestFileLinkTarget.txt'
#     filenameAOrig='20160825TestFile.org.original'  #these are never to be overwritten
#     filenameBOrig='20160825TestFileLinkTarget.txt.original'

#     assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
#     assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

#     #don't want to lose a valuable existing database
#     restoreDatabase=False
#     if os.path.exists(databaseName):
#         os.rename(databaseName,databaseName+'.bak')
#         restoreDatabase=True

#     blurbList=['fileB is a non org file']
#     blurbList.extend(['fileB is moved to another folder','basename of fileB is changed','broken link to fileB in fileA is repaired'])
#     blurbList.extend(['fileA is edited so that repaired link to fileB is back to the original value','repair of this broken link tests previous filename repair capability'])
#     blurb1="\n".join(blurbList)
#     print blurb1

#     print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
#     if runWithPauses:
#         wait_on_user_input('Now pausing to review nature of test')

#     #####################################################

#     print 'Now analyzing fileA %s; unique ID will be inserted' % filenameA
    
#     showLog1=True
#     fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

#     #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
#     assert len(fileA.linksToNonOrgFilesList)==1, 'fileA does not have a single link to a non org file'
#     assert fileA.linksToNonOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

#     if runWithPauses and (not showLog1):
#         wait_on_user_input()
    
#     #####################################################

#     origFolder=os.path.split(fileA.filenameAP)[0]
    
#     #move and rename fileB
#     newNameB=os.path.join(anotherFolder,'NoName.txt')
#     os.rename(filenameB,newNameB)
#     print 'Just moved fileB %s to %s' % (filenameB,newNameB)

#     #####################################################

#     #OOPS it is not possible to repair a link to a non org file that has been renamed

#     print 'Now analyzing fileA %s again; look for successful repair of link to fileB' % filenameA

#     showLog1=True
#     fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

#     # assert fileA.linksToNonOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

#     if fileA.linksToNonOrgFilesList[0].targetObj.repaired:
#         print 'Link in fileA to fileB was repaired successfully'
#     else:
#         print 'Link in fileA to fileB is still broken; test failed'
#         testPasses=False

#     expectedRepairMethod='attemptRepairByLookingInsideFilesForUniqueID'
#     repairMethod=fileA.linksToNonOrgFilesList[0].targetObj.repairedVia

#     if repairMethod==expectedRepairMethod:
#         print 'Repair method was %s as expected' % expectedRepairMethod
#     else:
#         print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
#         testPasses=False

#     if runWithPauses and (not showLog1):
#         wait_on_user_input()

#     #####################################################
#     #wish to change fileA such that link points to old fileB
#     #cannot simply do this since there will be a unique ID mismatch and script will quit:
#     # shutil.copy2(filenameAOrig,filenameA)
#     # print 'Just replaced fileA with original fileA; link now points to old name of fileB'
#     #must generate test file from current fileA so that unique ID matches the one in current fileA

#     inp=file(filenameA,'r')
#     oldLines2=[a for a in inp.readlines() if a.strip()]  #gets rid of lines that are just a newline \n character
#     oldLines2[-1]=oldLines2[-1].replace(newNameB,filenameB)  #change the one outward link in filenameA to point to previous name of filenameB
#     #20160901: oops: script had given link a description that matches new name; does not seem worth the trouble to erase this description
#     inp.close()
#     out=file(filenameA,'w')
#     out.writelines(oldLines2)
#     out.close()

#     print 'Just rewrote fileA so that link points to previous name of fileB'

#     #####################################################

#     print 'Now analyzing fileA %s again; look for successful repair of link to fileB' % filenameA

#     showLog1=True
#     fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

#     if fileA.linksToNonOrgFilesList[0].targetObj.repaired:
#         print 'Link in fileA to fileB was repaired successfully'
#     else:
#         #actually you have not checked if link is working or not
#         print 'Link in fileA to fileB is still broken; test failed'
#         testPasses=False

#     expectedRepairMethod='attemptRepairUsingTablePreviousFilenames'
#     repairMethod=fileA.linksToNonOrgFilesList[0].targetObj.repairedVia

#     if repairMethod==expectedRepairMethod:
#         print 'Repair method was %s as expected' % expectedRepairMethod
#     else:
#         print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
#         testPasses=False

#     if runWithPauses and (not showLog1):
#         wait_on_user_input()

#     #####################################################
    
#     print 'Finally, restoring files on disk to original configuration; deleting database\n'

#     os.remove(newNameB)
#     os.remove(databaseName)
#     shutil.copy2(filenameAOrig,filenameA)
#     shutil.copy2(filenameBOrig,filenameB)

#     if restoreDatabase:
#         os.rename(databaseName+'.bak',databaseName)

#     return testPasses

def test05B(runDebuggerOnlyInRepairStep=False,runDebuggerInEveryStep=False,runWithPauses=True):
    '''
    fileA links to symlink that points to fileB
    fileB is an non org file
    analyze fileA to build database
    edit fileA so that single link is again to the symlink
    change name of symlink on disk so script can't find it
    repair broken link in fileA via symlinks table method
    '''

    #TODO this script could create these two files on disk, and put the desired contents in them; seems like too much coding effort?
    databaseName='orgFiles.sqlite'
    filenameA='20160825TestFile.org'
    filenameB='20160825TestFileLinkTarget.txt'
    filenameAOrig='20160825TestFile.org.original'  #these are never to be overwritten
    filenameBOrig='20160825TestFileLinkTarget.txt.original'

    assert os.path.exists(filenameA), 'fileA %s does not exist on disk' % filenameA
    assert os.path.exists(filenameB), 'fileB %s does not exist on disk' % filenameB

    #don't want to lose a valuable existing database
    restoreDatabase=False
    if os.path.exists(databaseName):
        os.rename(databaseName,databaseName+'.bak')
        restoreDatabase=True

    blurbList=['fileA links to symlink that points to fileB','fileB is a non org file','analyze fileA to build database']
    blurbList.extend(['edit fileA so that single link is again to the symlink','change name of symlink on disk so script cannot find it','repair broken link in fileA via symlinks table method'])
    blurb1="\n".join(blurbList)
    print blurb1

    print 'fileA is %s and fileB is %s' % (filenameA,filenameB)
    
    if runWithPauses:
        wait_on_user_input('Now pausing to review nature of test')

    #####################################################

    print 'Now analyzing fileA %s' % filenameA
    print 'This will replace link to symlink that points to fileB, with link directly to fileB'    
    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=runDebuggerInEveryStep,isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    #have an urge to do automatic cleanup if these assert statements end the program, but if fileA was not right to begin with, need to do manual cleanup
    assert len(fileA.linksToNonOrgFilesList)==1, 'fileA does not have a single link to a non org file'
    assert fileA.linksToNonOrgFilesList[0].targetObj.filenameAP==os.path.join(os.getcwd(),filenameB), 'link to fileB is not found in fileA'

    if runWithPauses and (not showLog1):
        wait_on_user_input()

    #####################################################
    #change fileA such that link points to symlink to old fileB

    symlinkB='symlinkTo'+filenameB

    # this will not detect if symlinkB is gone from disk, because broken symlink fails os.path.exists
    # assert os.path.exists(symlinkB), 'Symlink %s is missing; cannot proceed with Test 12' % symlinkB
    assert os.path.islink(symlinkB), 'Symlink %s is missing; cannot proceed with Test 12' % symlinkB

    inp=file(filenameA,'r')
    oldLines2=[a for a in inp.readlines() if a.strip()]  #gets rid of lines that are just a newline \n character
    oldLines2[-1]=oldLines2[-1].replace(filenameB,symlinkB)  #change the one outward link in filenameA to point to previous symlink to fileB
    inp.close()
    out=file(filenameA,'w')
    out.writelines(oldLines2)
    out.close()

    print 'Just rewrote fileA so that link points to symlink that points to fileB'

    #must do this or else script will convert symlink into what it points to, which would prevent repair by symlinks table
    tempSymlinkB=symlinkB+'.temp'
    os.rename(symlinkB,tempSymlinkB)

    #####################################################

    print 'Now analyzing fileA %s again; look for successful repair of link to fileB' % filenameA

    showLog1=True
    fileA=operate_on_fileA_w(filenameA,runDebugger=(runDebuggerOnlyInRepairStep or runDebuggerInEveryStep),isDryRun=False,showLog=(showLog1 and runWithPauses),runWPauses=runWithPauses)

    # assert fileA.linksToOrgFilesList[0].targetObj.repaired, 'broken link in fileA was not repaired; test fails'

    if fileA.linksToNonOrgFilesList[0].targetObj.repaired:
        print 'Link in fileA to fileB was repaired successfully'
        testPasses=True
    else:
        print 'Link in fileA to fileB is still broken; test failed'
        testPasses=False

    expectedRepairMethod='attemptRepairUsingSymlinksTable'
    repairMethod=fileA.linksToNonOrgFilesList[0].targetObj.repairedVia

    if repairMethod==expectedRepairMethod:
        print 'Repair method was %s as expected' % expectedRepairMethod
    else:
        print 'Repair method %s is different than expected %s; test failed' % (repairMethod,expectedRepairMethod)
        testPasses=False

    if runWithPauses and (not showLog1):
        wait_on_user_input()
    
    #####################################################

    print 'Finally, restoring files on disk to original configuration; deleting database\n'

    os.remove(databaseName)
    os.rename(tempSymlinkB,symlinkB)
    shutil.copy2(filenameAOrig,filenameA)
    shutil.copy2(filenameBOrig,filenameB)

    if restoreDatabase:
        os.rename(databaseName+'.bak',databaseName)

    return testPasses

#head module level stuff
# OFL.set_up_logging('debug')  #do not log at debug level or below
OFL.set_up_logging()  #log at all levels
#head files for test of repair of links to org file
filename1='20160817TestFile.org'
filename2='20160817TestFileLinkTarget.org'
filename1Orig='20160817TestFile.org.original'  #these are never to be overwritten
filename2Orig='20160817TestFileLinkTarget.org.original'
#head files for test of repair of links to non-org file
filename3='20160825TestFile.org'
filename4='20160825TestFileLinkTarget.txt'
filename3Orig='20160825TestFile.org.original'  #these are never to be overwritten
filename4Orig='20160825TestFileLinkTarget.txt.original'
#head
for file1 in [filename1,filename2,filename1Orig,filename2Orig,filename3,filename4,filename3Orig,filename4Orig]:
    assert os.path.exists(file1), 'file %s does not exist on disk' % file1
shutil.copy2(filename1Orig,filename1)
shutil.copy2(filename2Orig,filename2)
shutil.copy2(filename3Orig,filename3)
shutil.copy2(filename4Orig,filename4)
#head set up a test folder (a place to move certain test files to as part of test)
DocumentsFolderAP=os.path.join(os.path.expanduser('~'),'Documents')
assert os.path.exists(DocumentsFolderAP), 'Cannot proceed since assuming the folder %s exists' % DocumentsFolderAP
anotherFolder=os.path.join(DocumentsFolderAP,'TempOFLTests1','TempOFLTests2','TempOFLTests3')
if not os.path.exists(anotherFolder):
    os.makedirs(anotherFolder)
assert os.path.exists(anotherFolder), 'Cannot proceed since assuming the folder %s exists' % anotherFolder
#head
#head MAIN
if __name__=="__main__":
    #TODO change to command line inputs.  inputs: which test to run, logging level, runDebuggerOnlyInRepairStep, runWithPauses
    # pudb.set_trace()
    runDebuggerOnlyInRepairStep=False
    runDebuggerInEveryStep=False
    runWithPauses=False

    # testsToRun=[test01,test02,test03,test04,test05,test06,test07,test08,test09,test10,test11,test12]  #links to org file
    testsToRun=[test01,test02,test03,test04,test05,test06,test07,test08,test09,test10]  #links to org file
    testsToRun+=[test01B,test02B,test03B,test05B]  #links to non org file

    #test04B: this one is broken; not obvious how to construct this test
    #test11: appears broken 20160930; unsure how to write it so that desired repair method is used
    #test12: appears broken 20160930; unsure how to write it so that desired repair method is used

    # testsToRun=[test01]  # do just one

    testResultsTF=[]

    for test in testsToRun:
        testResultsTF.append((test.__name__,test(runDebuggerOnlyInRepairStep=runDebuggerOnlyInRepairStep,runDebuggerInEveryStep=runDebuggerInEveryStep,runWithPauses=runWithPauses)))  #list of tuples
        print "%s passes (T/F): %s" % testResultsTF[-1]

    print 'All test results pass: %s' % all([a[1] for a in testResultsTF])
