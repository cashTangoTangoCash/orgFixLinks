import unittest
import orgFixLinks as OFL
import datetime
import os

#TODO test regexOrderedList, or part of larger test?
#TODO test regexDict, or part of larger test?
#TODO test OrgFile.myUniqueIDRegex, or part of larger test?

#TODO merge this with previous test file?  no, that file seems too specialized

#TODO test that unique ID generator makes unique IDs that are detected by appropriate regex

#TODO test converting a line into list of objects, than back into the same line (catch bug that is adding spaces)

#TODO trying to change orgFixLinks.py so that can import from it and test things, but look out for .bak backing up of key files!

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
    #head TODO there are a number of things to test in LocalFile.__init__
    #head test LocalFile.testIfExists
    def test1_testIfExists(self):
        '''test LocalFileMethods.testIfExists '''

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
        '''test LocalFileMethods.testIfExists '''

        orgFile=OFL.OrgFile('fileThatDoesNotExist.org',inHeader=False)
        self.failIf(orgFile.testIfExists())

    #head test LocalFile.testIfExistsSymlinkVersion
    #head TODO test LocalFile.testIfExistsSymlinkVersion; python can create a symlink; see main org file
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


#head
DocumentsFolderAP=os.path.join(os.path.expanduser('~'),'Documents')
assert os.path.exists(DocumentsFolderAP), 'Cannot proceed since assuming the folder %s exists' % DocumentsFolderAP
anotherFolder=os.path.join(DocumentsFolderAP,'TempOFLTests1','TempOFLTests2','TempOFLTests3')
if not os.path.exists(anotherFolder):
    os.makedirs(anotherFolder)
assert os.path.exists(anotherFolder), 'Cannot proceed since assuming the folder %s exists' % anotherFolder
#head
if __name__ == "__main__":
    unittest.main()
