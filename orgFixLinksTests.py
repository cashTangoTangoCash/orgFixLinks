import unittest
import orgFixLinks as OFL
import datetime
import os

#TODO merge this with previous test file?  no, that file seems too specialized

#TODO test regexOrderedList, or part of larger test?
#TODO test regexDict, or part of larger test?
#TODO test OrgFile.myUniqueIDRegex, or part of larger test?

#TODO test that unique ID generator makes unique IDs that are detected by appropriate regex

#TODO test converting a line into list of objects, than back into the same line (catch bug that is adding spaces)

#TODO because of the way the script under test is written, it seems difficult to write true unit tests

#TODO test lookInsideForUniqueID when there is a full representation of an org file

#TODO test the many sqlite database operations

#head test functions inside classes
class TestNodeMethods(unittest.TestCase):
    def test1_findUniqueID(self):
        '''test Node.findUniqueID (uniqueIDRegexObj is set to OrgFile.myUniqueIDRegex)'''

        testLines1=['* status\n','#MyUniqueID2016-05-19_17-15-59-9812   \n']
        node1=OFL.Node(testLines1,sourceFile=None)
        node1.findUniqueID(OFL.OrgFile.myUniqueIDRegex)
        self.failUnless(node1.uniqueID)
        self.assertEqual(node1.uniqueID,'2016-05-19_17-15-59-9812')

    def test2_findUniqueID(self):
        '''test Node.findUniqueID (uniqueIDRegexObj set to OrgFile.myUniqueIDRegex)'''

        testLines1=['* status\n','** #MyUniqueID2016-05-19_17-15-59-9812   \n']
        node1=OFL.Node(testLines1,sourceFile=None)
        node1.findUniqueID(OFL.OrgFile.myUniqueIDRegex)
        self.failIf(node1.uniqueID)

class TestLocalFileMethods(unittest.TestCase):
    #head TODO is there anything to test in LocalFile.__init__?  seems like no.
    #head test LocalFile.testIfExists
    def test1_testIfExists(self):
        '''test LocalFileMethods.testIfExists'''

        #put a file on disk; file is known to exist
        testFileLines=['* status\n']
        testFileLines.append('blurb\n')
        testFilename=datetime.datetime.now().strftime('%Y%m%d_%H%MTest.org')
        testFile=open(testFilename,'w')
        testFile.writelines(testFileLines)
        testFile.close()

        orgFile=OFL.OrgFile(testFilename,inHeader=False)
        self.failUnless(orgFile.testIfExists())
        os.remove(testFilename)

    def test2_testIfExists(self):
        '''test LocalFileMethods.testIfExists'''

        orgFile=OFL.OrgFile('fileThatDoesNotExist.org',inHeader=False)
        self.failIf(orgFile.testIfExists())

    def test3_testIfExists(self):
        '''test LocalFileMethods.testIfExists'''

        #put a file on disk; file is known to exist
        #put file in different folder than current working directory
        testFileLines=['* status\n']
        testFileLines.append('blurb\n')
        testFilename=os.path.join(anotherFolder,datetime.datetime.now().strftime('%Y%m%d_%H%MTest.org'))
        testFile=open(testFilename,'w')
        testFile.writelines(testFileLines)
        testFile.close()

        orgFile=OFL.OrgFile(testFilename,inHeader=False)
        self.failUnless(orgFile.testIfExists())
        os.remove(testFilename)

    #head test LocalFile.testIfExistsSymlinkVersion
    #head TODO test LocalFile.testIfExistsSymlinkVersion; python can create a symlink; see main org file google python repair symlink; webarnes.ca link; my file link-fixDDCommented.py
    def test1_testSymlinkHandling(self):
        '''test LocalFileMethods handling of symlinks'''
  
        #create a file on disk to be a symlink target
        testFileLines=['* status\n']
        testFileLines.append('blurb\n')
        testFilename=os.path.join(anotherFolder,datetime.datetime.now().strftime('%Y%m%d_%H%MTest.org'))
        testFile=open(testFilename,'w')
        testFile.writelines(testFileLines)
        testFile.close()

        testTarget=OFL.OrgFile(testFilename,inHeader=False)

        #make a symlink that points to the first file
        symlinkFilename=os.path.join(anotherFolder2,datetime.datetime.now().strftime('%Y%m%d_%H%MTestSymlink.org'))
        os.symlink(testFilename,symlinkFilename) #target comes first

        testSymlink=OFL.OrgFile(symlinkFilename,inHeader=False,leaveAsSymlink=True)  #leaveAsSymlink is False in normal operation of orgFixLinks.py

        self.failUnless(testSymlink.exists)  #symlink exists; it would exist even if target were missing
        self.failIf(testSymlink.changedFromSymlinkToNonSymlink) #because leaveAsSymlink=True
        self.assertEqual(testSymlink.targetFilenameAP,testTarget.filenameAP)
        self.failUnless(testSymlink.targetExists)
        self.failUnless(testSymlink.isSymlink)
        self.failIf(testSymlink.isBrokenSymlink)

        os.remove(testFilename)
        os.remove(symlinkFilename)

    def test2_testSymlinkHandling(self):
        '''test LocalFileMethods handling of symlinks'''

        #create a file on disk; it will be symlink target
        testFileLines=['* status\n']
        testFileLines.append('blurb\n')
        testFilename=os.path.join(anotherFolder,datetime.datetime.now().strftime('%Y%m%d_%H%MTest.org'))
        testFile=open(testFilename,'w')
        testFile.writelines(testFileLines)
        testFile.close()

        testTarget=OFL.OrgFile(testFilename,inHeader=False)

        #make a symlink that points to the first file
        symlinkFilename=os.path.join(anotherFolder2,datetime.datetime.now().strftime('%Y%m%d_%H%MTestSymlink.org'))
        os.symlink(testFilename,symlinkFilename) #target comes first

        #delete target after making symlink to it
        os.remove(testFilename)
        testTarget.testIfExists()
        self.failIf(testTarget.exists)

        testSymlink=OFL.OrgFile(symlinkFilename,inHeader=False,leaveAsSymlink=True)  #leaveAsSymlink=False in normal operation of orgFixLinks.py

        #even though link target is missing, my code says the link itself exists
        self.failUnless(testSymlink.exists)

        self.failIf(testSymlink.targetExists) #it is the target that does not exist
        self.failIf(testSymlink.changedFromSymlinkToNonSymlink) #because leaveAsSymlink=True
        self.assertEqual(testSymlink.targetFilenameAP,testTarget.filenameAP)

        self.failUnless(testSymlink.isSymlink)
        self.failUnless(testSymlink.isBrokenSymlink) #because its target was deleted before instantiating it

        os.remove(symlinkFilename)

    def test3_testSymlinkHandling(self):
        '''test LocalFileMethods handling of symlinks'''
        #create a file on disk; it will be symlink target
        testFileLines=['* status\n']
        testFileLines.append('blurb\n')
        testFilename=os.path.join(anotherFolder,datetime.datetime.now().strftime('%Y%m%d_%H%MTest.org'))
        testFile=open(testFilename,'w')
        testFile.writelines(testFileLines)
        testFile.close()

        testTarget=OFL.OrgFile(testFilename,inHeader=False)

        #make a symlink that points to the first file
        symlinkFilename=os.path.join(anotherFolder2,datetime.datetime.now().strftime('%Y%m%d_%H%MTestSymlink.org'))
        os.symlink(testFilename,symlinkFilename) #target comes first

        testSymlink=OFL.OrgFile(symlinkFilename,inHeader=False,leaveAsSymlink=False)  #it is replaced with its target

        self.failUnless(testSymlink.exists) #was replaced with its target and target exists
        self.failUnless(testSymlink.changedFromSymlinkToNonSymlink) #because leaveAsSymlink=False
        self.assertEqual(testSymlink.filenameAP,testTarget.filenameAP) #because leaveAsSymlink=False
        # self.failUnless(testSymlink.targetExists)  # TODO have not decided what value this should have
        self.failIf(testSymlink.isSymlink) #because leaveAsSymlink=False
        # self.failIf(testSymlink.isBrokenSymlink) # TODO have not decided what value this should have 
        #TODO have not decided what testSymlink.targetFilenameAP should be; target of symlink is already stored in testSymlink.filenameAP
        self.assertEqual(testSymlink.originalFilenameAP,symlinkFilename)
        self.assertEqual(testSymlink.originalTargetFilenameAP,testSymlink.filenameAP)

        os.remove(testFilename)
        os.remove(symlinkFilename)

    def test4_testSymlinkHandling(self):
        '''test LocalFileMethods handling of symlinks'''

        #create a file on disk; it will be target of symlink
        testFileLines=['* status\n']
        testFileLines.append('blurb\n')
        testFilename=os.path.join(anotherFolder,datetime.datetime.now().strftime('%Y%m%d_%H%MTest.org'))
        testFile=open(testFilename,'w')
        testFile.writelines(testFileLines)
        testFile.close()

        testTarget=OFL.OrgFile(testFilename,inHeader=False)

        #make a symlink that points to that test file
        symlinkFilename=os.path.join(anotherFolder2,datetime.datetime.now().strftime('%Y%m%d_%H%MTestSymlink.org'))
        os.symlink(testFilename,symlinkFilename) #target comes first

        #delete target after making symlink to it
        os.remove(testTarget.filenameAP)
        testTarget.testIfExists()
        self.failIf(testTarget.exists)

        testSymlink=OFL.OrgFile(symlinkFilename,inHeader=False,leaveAsSymlink=False) #symlink is replaced with target

        self.failIf(testSymlink.exists) #target was deleted
        self.failUnless(testSymlink.changedFromSymlinkToNonSymlink)
        self.assertEqual(testSymlink.filenameAP,testTarget.filenameAP)
        # self.failIf(testSymlink.targetExists)
        self.failIf(testSymlink.isSymlink)
        # self.failUnless(testSymlink.isBrokenSymlink)
        #TODO have not decided what testSymlink.targetFilenameAP should be; target of symlink is already stored in testSymlink.filenameAP
        self.assertEqual(testSymlink.originalFilenameAP,symlinkFilename)
        self.assertEqual(testSymlink.originalTargetFilenameAP,testSymlink.filenameAP)

        os.remove(symlinkFilename)

    #head TODO could write a test with a target, a first symlink pointing to it, and a 2nd symlink pointing to first symlink.  delete the 1st two files; now what about symlink #2?
    #head for me this rarely occurs in real life
class TestOrgFileMethods(unittest.TestCase):
    def test1_endsInDotOrg(self):
        '''test OrgFile.endsInDotOrg'''
        filenameAP=os.path.join(DocumentsFolderAP,'fakeFile.org')
        orgFile=OFL.OrgFile(filenameAP,inHeader=False)
        self.failUnless(orgFile.endsInDotOrg())

    def test2_endsInDotOrg(self):
        '''test OrgFile.endsInDotOrg'''
        filenameAP=os.path.join(DocumentsFolderAP,'fakeFile.txt')
        orgFile=OFL.OrgFile(filenameAP,inHeader=False)
        self.failIf(orgFile.endsInDotOrg())

    #head TODO test useDatabaseToGetOutwardLinks
    #head TODO test createFullRepresentation; expecting this to be not easy
#head test standalone functions
class TestGetAsteriskLevelFunction(unittest.TestCase):
    def test1(self):
        '''test get_asterisk_level'''
        line='* junk text\n'
        self.assertEqual(OFL.get_asterisk_level(line),1)

    def test2(self):        
        '''test get_asterisk_level'''
        line='*** junk text\n'
        self.assertEqual(OFL.get_asterisk_level(line),3)

    def test3(self):        
        '''test get_asterisk_level'''
        line='junk text\n'
        self.assertEqual(OFL.get_asterisk_level(line),0)

    def test4(self):        
        '''test get_asterisk_level'''
        line='junk *** text ***\n'
        self.assertEqual(OFL.get_asterisk_level(line),0)

class TestFindUniqueIDInsideFileFunction(unittest.TestCase):
    '''these are all tests of OFL.find_unique_id_inside_org_file
    which is a function that goes line by line inside an org file
    it's used when script has not made a full representation of that org file
    '''
    def test1(self):
        '''test find_unique_id_inside_file: file contains status node but does not contain unique ID'''
        
        testFileLines=['* status\n']
        testFileLines.append('blurb\n')
        testFilename=datetime.datetime.now().strftime('%Y%m%d_%H%MTest.org')
        testFile=open(testFilename,'w')
        testFile.writelines(testFileLines)
        testFile.close()

        uniqueID=OFL.find_unique_id_inside_org_file(testFilename)
        self.failIf(uniqueID)
        os.remove(testFilename)

    def test2(self):
        '''test find_unique_id_inside_file: file contains status node but does not contain unique ID'''
        
        testFileLines=['* status\n']
        testFileLines.append('#MyUniqueID2016-05-19_17-15-59-9812   \n')
        testFilename=datetime.datetime.now().strftime('%Y%m%d_%H%MTest.org')
        testFile=open(testFilename,'w')
        testFile.writelines(testFileLines)
        testFile.close()

        uniqueID=OFL.find_unique_id_inside_org_file(testFilename)
        self.assertEqual(uniqueID,'2016-05-19_17-15-59-9812')
        os.remove(testFilename)

    def test3(self):
        '''test find_unique_id_inside_file: file contains status node but does not contain unique ID'''
        
        testFileLines=['* status\n']
        testFileLines.append('#MyUniqueID2016-05-19_17-15-59-9812   \n')
        testFileLines.append('#MyUniqueID2016-05-19_17-15-59-9813   \n')
        testFilename=datetime.datetime.now().strftime('%Y%m%d_%H%MTest.org')
        testFile=open(testFilename,'w')
        testFile.writelines(testFileLines)
        testFile.close()

        uniqueID=OFL.find_unique_id_inside_org_file(testFilename)
        self.assertEqual(uniqueID,'2016-05-19_17-15-59-9812')
        os.remove(testFilename)

    def test4(self):
        '''test find_unique_id_inside_file: file contains status node but does not contain unique ID'''
        
        testFileLines=[]
        testFileLines.append('#MyUniqueID2016-05-19_17-15-59-9812   \n')
        testFileLines.append('#MyUniqueID2016-05-19_17-15-59-9813   \n')
        testFilename=datetime.datetime.now().strftime('%Y%m%d_%H%MTest.org')
        testFile=open(testFilename,'w')
        testFile.writelines(testFileLines)
        testFile.close()

        uniqueID=OFL.find_unique_id_inside_org_file(testFilename)
        self.failIf(uniqueID)
        os.remove(testFilename)

    def test5(self):
        '''test find_unique_id_inside_file: file contains status node but does not contain unique ID'''
        testFileLines=['one line\n','another line\n']
        testFileLines.append('* status\n')
        testFileLines.append('#MyUniqueID2016-05-19_17-15-59-9812   \n')
        testFilename=datetime.datetime.now().strftime('%Y%m%d_%H%MTest.org')
        testFile=open(testFilename,'w')
        testFile.writelines(testFileLines)
        testFile.close()

        uniqueID=OFL.find_unique_id_inside_org_file(testFilename)
        self.assertEqual(uniqueID,'2016-05-19_17-15-59-9812')
        os.remove(testFilename)


class TestListOfChildNodesFromLines(unittest.TestCase):
    def test1(self):
        pass
#head
DocumentsFolderAP=os.path.join(os.path.expanduser('~'),'Documents')
assert os.path.exists(DocumentsFolderAP), 'Cannot proceed since assuming the folder %s exists' % DocumentsFolderAP
anotherFolder=os.path.join(DocumentsFolderAP,'TempOFLTests1','TempOFLTests2','TempOFLTests3')
if not os.path.exists(anotherFolder):
    os.makedirs(anotherFolder)
assert os.path.exists(anotherFolder), 'Cannot proceed since assuming the folder %s exists' % anotherFolder
anotherFolder2=os.path.join(DocumentsFolderAP,'TempOFLTests1','TempOFLTests2')
#head
if __name__ == "__main__":
    unittest.main()
