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
class TestLinkMethods(unittest.TestCase):
    def test1(self):
        pass

class TestLinkToLocalFileMethods(unittest.TestCase):
    def test1(self):
        pass

class TestLinkToNonOrgFileMethods(unittest.TestCase):
    def test1(self):
        pass

class TestLinkToOrgFileMethods(unittest.TestCase):
    def test1(self):
        pass

#head
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

    #head TODO could init a node with some tags, some org file links, some non org file links, and then test the lists came out right
#head
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
class TestAllUpperToAllLowercase(unittest.TestCase):
    def test1(self):
        someText='I AM ALL UPPER CASE'
        result='i am all upper case'
        self.assertEqual(OFL.all_upper_to_all_lowercase(someText),result)

    def test2(self):
        someText='I AM not ALL UPPER CASE'
        result=someText
        self.assertEqual(OFL.all_upper_to_all_lowercase(someText),result)

class TestGetAsteriskLevel(unittest.TestCase):
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

class TestGetBaseAsteriskLevel(unittest.TestCase):
    def test1(self):
        '''test get_base_asterisk_level'''
        lines=['line1\n','line2\n','line3\n']
        self.assertEqual(OFL.get_base_asterisk_level(lines),0)

    def test2(self):
        '''test get_base_asterisk_level'''
        lines=['* line1\n','line2\n','line3\n']
        self.assertEqual(OFL.get_base_asterisk_level(lines),1)

    def test3(self):
        '''test get_base_asterisk_level'''
        lines=['* line1\n','** line2\n','*** line3\n']
        self.assertEqual(OFL.get_base_asterisk_level(lines),1)

    def test4(self):
        '''test get_base_asterisk_level'''
        lines=['*** line1\n','** line2\n','* line3\n']
        self.assertEqual(OFL.get_base_asterisk_level(lines),1)

    def test5(self):
        '''test get_base_asterisk_level'''
        lines=['*** line1\n','line2\n','** line3\n','line4\n','* line5\n','line6\n']
        self.assertEqual(OFL.get_base_asterisk_level(lines),1)

    def test6(self):
        '''test get_base_asterisk_level'''
        lines=['***   line1\n','**   line2\n','**   line3\n']  #extra spaces after leading asterisks
        self.assertEqual(OFL.get_base_asterisk_level(lines),2)

class TestFindUniqueIDInsideFile(unittest.TestCase):
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


class TestSeparateParentLinesDescendantLines(unittest.TestCase):
    def test1(self):
        '''test separate_parent_lines_descendant_lines'''
        lines=['* line1','** line2','*** line3']
        parentLines,descendantLines=OFL.separate_parent_lines_descendant_lines(lines)
        self.assertEqual(parentLines,['* line1'])
        self.assertEqual(descendantLines,['** line2','*** line3'])

    def test2(self):
        '''test separate_parent_lines_descendant_lines'''
        lines=['line1','line2','line3']
        parentLines,descendantLines=OFL.separate_parent_lines_descendant_lines(lines)
        self.assertEqual(parentLines,lines)
        self.assertEqual(descendantLines,None)

    def test3(self):
        '''test separate_parent_lines_descendant_lines'''
        lines=['* line1','line2','line3']
        parentLines,descendantLines=OFL.separate_parent_lines_descendant_lines(lines)
        self.assertEqual(parentLines,lines)
        self.assertEqual(descendantLines,None)

    def test4(self):
        '''test separate_parent_lines_descendant_lines'''
        lines=['* line1','line2','** line3','line 4']
        parentLines,descendantLines=OFL.separate_parent_lines_descendant_lines(lines)
        self.assertEqual(parentLines,['* line1','line2'])
        self.assertEqual(descendantLines,['** line3','line 4'])

class TestListOfChildNodesFromLines(unittest.TestCase):
    def test1(self):
        '''test list_of_child_nodes_from_lines: no line starts with asterisk'''
        lines=['first\n','second\n','third\n']
        childNodeList=OFL.list_of_child_nodes_from_lines(lines,sourceFile=None)
        self.assertEqual([],childNodeList)

    #TODO fill in more tests; first review Node.__init__

class TestLineToList1(unittest.TestCase):
    def test1(self):
        line='some text [[a link with brackets]] more text [[another link with brackets][description]].'
        outputList=['some text ','[[a link with brackets]]',' more text ','[[another link with brackets][description]]','.']  #note the spaces
        self.assertEqual(OFL.line_to_list1(line),outputList)

    def test2(self):
        line='some text [[a link with brackets]] more text [[another link with brackets][description]].\n'
        outputList=['some text ','[[a link with brackets]]',' more text ','[[another link with brackets][description]]','.']  #note the spaces, and \n is gone
        self.assertEqual(OFL.line_to_list1(line),outputList)

    def test3(self):
        line='some text [[a link with brackets]] more text [[another link with brackets][description]].  \n'
        outputList=['some text ','[[a link with brackets]]',' more text ','[[another link with brackets][description]]','.  ']  #note the spaces, and \n is gone
        self.assertEqual(OFL.line_to_list1(line),outputList)

class TestTextToLinkAndDescriptionDoubleBrackets(unittest.TestCase):
    def test1(self):
        someText='[[link link]]'
        link,description=OFL.text_to_link_and_description_double_brackets(someText)
        self.assertEqual('link link',link)
        self.assertEqual(None,description)

    def test2(self):
        someText='[[ link link ][ descr descr ]]'
        link,description=OFL.text_to_link_and_description_double_brackets(someText)
        self.assertEqual(' link link ',link)
        self.assertEqual(' descr descr ',description)

class TestFindBestRegexMatchForText(unittest.TestCase):
    #head this is where you test if your regexes can correctly identify links
    #head temp lines for copy and paste:
    # self.assertEqual(matchingRegex,OFL.LinkToOrgFile.linkRegexes['file:anyFilename.org::anything or file+sys:anyFilename.org::anything or file+emacs:anyFilename.org::anything or docview:anyFilename.org::anything'])
    # self.assertEqual(matchingRegex,OFL.LinkToOrgFile.linkRegexes['/anyFilename.org::anything  or  ./anyFilename.org::anything  or  ~/anyFilename.org::anything'])
    # self.assertEqual(matchingRegex,OFL.LinkToOrgFile.linkRegexes['file:anyFilename.org or file+sys:anyFilename.org or file+emacs:anyFilename.org or docview:anyFilename.org'])
    # self.assertEqual(matchingRegex,OFL.LinkToOrgFile.linkRegexes['/anyFilename.org  or  ./anyFilename.org  or  ~/anyFilename.org'])

    # self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['file:anyFilename::anything or file+sys:anyFilename::anything or file+emacs:anyFilename::anything or docview:anyFilename::anything'])
    # self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['/anyFilename::anything  or  ./anyFilename::anything  or  ~/anyFilename::anything'])
    # self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename'])
    # self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['/anyFilename  or  ./anyFilename  or  ~/anyFilename'])

    def test1(self):
        '''some non-link text'''
        #see OFL.Node.__init__
        #at the point that OFL.find_best_regex_match_for_text is called, its argument would not have the link bracket pattern, or spaces
        someText='not_link_text'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(someText)
        self.failIf(matchingRegex)

    def test2(self):
        '''an internal link'''
        someText='#my-custom-id'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(someText)
        self.failIf(matchingRegex)

    def test3(self):
        '''an internal link'''
        someText='id:B7423F4D-2E8A-471B-8810-C40F074717E9'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(someText)
        self.failIf(matchingRegex)

    def test4(self):
        '''a web link'''
        someText='http://www.astro.uva.nl/~dominik'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(someText)
        self.failIf(matchingRegex)

    def test5(self):
        '''a document identifier'''
        someText='doi:10.1000/182'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(someText)
        self.failIf(matchingRegex)

    def test6(self):
        link1='OrgModeFileCrawlerMain.org'  #without brackets, org will not detect it as a clickable link; with brackets, org sees it as an internal link
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.failIf(matchingRegex)

    def test7(self):
        link1='file:OrgModeFileCrawlerMain.org'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToOrgFile.linkRegexes['file:anyFilename.org or file+sys:anyFilename.org or file+emacs:anyFilename.org or docview:anyFilename.org'])
        self.assertEqual(matchingClass,OFL.LinkToOrgFile)

    def test8(self):
        link1='/OrgModeFileCrawlerMain.org'  #without brackets, org will not detect this as a clickable link
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToOrgFile.linkRegexes['/anyFilename.org  or  ./anyFilename.org  or  ~/anyFilename.org'])
        self.assertEqual(matchingClass,OFL.LinkToOrgFile)

    def test9(self):
        link1='file:/OrgModeFileCrawlerMain.org'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToOrgFile.linkRegexes['file:anyFilename.org or file+sys:anyFilename.org or file+emacs:anyFilename.org or docview:anyFilename.org'])
        self.assertEqual(matchingClass,OFL.LinkToOrgFile)

    def test10(self):
        link1='~/OrgModeFileCrawlerMain.org'  #without brackets, org will not detect this as a clickable link
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToOrgFile.linkRegexes['/anyFilename.org  or  ./anyFilename.org  or  ~/anyFilename.org'])
        self.assertEqual(matchingClass,OFL.LinkToOrgFile)

    def test11(self):
        link1='file:~/OrgModeFileCrawlerMain.org'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToOrgFile.linkRegexes['file:anyFilename.org or file+sys:anyFilename.org or file+emacs:anyFilename.org or docview:anyFilename.org'])
        self.assertEqual(matchingClass,OFL.LinkToOrgFile)

    def test12(self):
        link1='OrgModeFileCrawlerMain.org::what about' #without brackets, there could be no spaces in search term, and org won't see link as clickable.  with brackets, org sees link as an internal link
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.failIf(matchingRegex)

    def test13(self):
        link1='file:OrgModeFileCrawlerMain.org::what about' #with file in front, link will be clickable in org without brackets.  without brackets, search term cannot have spaces, since org will end the link at a space
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToOrgFile.linkRegexes['file:anyFilename.org::anything or file+sys:anyFilename.org::anything or file+emacs:anyFilename.org::anything or docview:anyFilename.org::anything'])
        self.assertEqual(matchingClass,OFL.LinkToOrgFile)

    def test14(self):
        #without brackets, org would not detect this as a clickable link
        link1=os.path.join(os.path.expanduser('~'),'Documents/Computer/Software/OrgModeNotes/MyOrgModeScripts/OrgModeFileCrawler/20160908ExceptionTest.py')
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['/anyFilename  or  ./anyFilename  or  ~/anyFilename'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test15(self):
        link1='file:'+os.path.join(os.path.expanduser('~'),'Documents/Computer/Software/OrgModeNotes/MyOrgModeScripts/OrgModeFileCrawler/20160908ExceptionTest.py')
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test16(self):
        link1='./20160908ExceptionTest.py' #without brackets, this link would not be clickable in org
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['/anyFilename  or  ./anyFilename  or  ~/anyFilename'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test17(self):
        link1='file:./20160908ExceptionTest.py'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test18(self):
        link1='./20160908Exception Test.py' #without brackets, this link would not be clickable in org
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['/anyFilename  or  ./anyFilename  or  ~/anyFilename'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test19(self):
        link1='file:./20160908Exception Test.py'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test20(self):
        link1='~/20160908ExceptionTest.py' #without brackets, this link would not be clickable in org
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['/anyFilename  or  ./anyFilename  or  ~/anyFilename'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test21(self):
        link1='file:~/20160908ExceptionTest.py'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test22(self):
        link1='20160908ExceptionTest.py' #without brackets, this link would not be clickable in org.  with brackets, org sees it as a clickable link.
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.failIf(matchingRegex)

    def test23(self):
        link1='file:20160908ExceptionTest.py'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test24(self):
        link1='PythonScriptOldVersions' #without brackets, this link would not be clickable in org.  with brackets, org sees it as a clickable link.
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.failIf(matchingRegex)

    def test25(self):
        link1='file:PythonScriptOldVersions'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test26(self):
        link1='/myself@some.where:papers/last.pdf' #do not want my script to detect this link to a file on a remote machine
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.failIf(matchingRegex)

    def test27(self):
        link1='file:/myself@some.where:papers/last.pdf' #do not want my script to detect this link to a file on a remote machine
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.failIf(matchingRegex)

    def test28(self):
        link1='20160908ExceptionTest.py::23' #if no brackets, org does not detect it as clickable link.  with brackets, org detects it as internal link.
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.failIf(matchingRegex)

    def test29(self):
        link1='file:20160908ExceptionTest.py::23'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['file:anyFilename::anything or file+sys:anyFilename::anything or file+emacs:anyFilename::anything or docview:anyFilename::anything'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test30(self):
        link1=os.path.join(os.path.expanduser('~'),'Documents/Computer/Software/PythonNotes/SeverancePythonForInformatics/PythonForInformaticsSeverance009d2.pdf')+'::32'  #not clickable in org without brackets
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['/anyFilename::anything  or  ./anyFilename::anything  or  ~/anyFilename::anything'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test31(self):
        link1='file:'+os.path.join(os.path.expanduser('~'),'Documents/Computer/Software/PythonNotes/SeverancePythonForInformatics/PythonForInformaticsSeverance009d2.pdf')+'::32'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['file:anyFilename::anything or file+sys:anyFilename::anything or file+emacs:anyFilename::anything or docview:anyFilename::anything'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test32(self):
        link1='OrgModeFileCrawlerMain.org::**what about'  #a heading search in an org file
        #without brackets, org will not see it as a clickable link.  with brackets, org sees it as internal link
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.failIf(matchingRegex)

    def test33(self):
        link1='file:OrgModeFileCrawlerMain.org::**what about'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToOrgFile.linkRegexes['file:anyFilename.org::anything or file+sys:anyFilename.org::anything or file+emacs:anyFilename.org::anything or docview:anyFilename.org::anything'])
        self.assertEqual(matchingClass,OFL.LinkToOrgFile)

    def test34(self):
        link1='file+sys:./20160807PuzzleOverProgramLogic.xoj'  #open via OS, like double-clicking
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test35(self):
        link1='file+emacs:./20160807PuzzleOverProgramLogic.xoj'  #force opening by emacs
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['file:anyFilename or file+sys:anyFilename or file+emacs:anyFilename or docview:anyFilename'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test36(self):
        link1='docview:'+os.path.join(os.path.expanduser('~'),'Documents/Computer/Software/PythonNotes/SeverancePythonForInformatics/PythonForInformaticsSeverance009d2.pdf')+'::32'
        matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
        self.assertEqual(matchingRegex,OFL.LinkToNonOrgFile.linkRegexes['file:anyFilename::anything or file+sys:anyFilename::anything or file+emacs:anyFilename::anything or docview:anyFilename::anything'])
        self.assertEqual(matchingClass,OFL.LinkToNonOrgFile)

    def test37(self):
        #long list of org mode links that orgFixLinks.py ignores
        link1List=[]

        link1='news:comp.emacs'  # usenet link;  does not require brackets; nothing happens when I try opening it in org mode
        link1List.append(link1)
        link1='mailto:adent@galaxy.net'  # mail link;  does not require brackets
        link1List.append(link1)
        link1='mhe:folder' # MH-E folder link
        link1List.append(link1)
        link1='mhe:folder#id' # MH-E message link
        link1List.append(link1)
        link1='rmail:folder' # RMAIL folder link
        link1List.append(link1)
        link1='rmail:folder#id' # RMAIL message link
        link1List.append(link1)
        link1='gnus:folder' # GNUS folder link
        link1List.append(link1)
        link1='gnus:folder#id' # GNUS message link
        link1List.append(link1)
        link1='gnus:group' # Gnus group link
        link1List.append(link1)
        link1='gnus:group#id' # Gnus article link
        link1List.append(link1)
        link1='bbdb:R.*Stallman' # BBDB link (with regexp)
        link1List.append(link1)
        link1='irc:/irc.com/#emacs/bob' # IRC link
        link1List.append(link1)
        link1='vm:folder' # VM folder link 
        link1List.append(link1)
        link1='vm:folder#id' # VM message link 
        link1List.append(link1)
        link1='vm://myself@some.where.org/folder#id' # VM on remote machine 
        link1List.append(link1)
        link1='vm-imap:account:folder' #VM IMAP folder link 
        link1List.append(link1)
        link1='vm-imap:account:folder#id' #VM IMAP message link 
        link1List.append(link1)
        link1='wl:folder' # WANDERLUST folder link
        link1List.append(link1)
        link1='wl:folder#id' # WANDERLUST message link
        link1List.append(link1)
        #might want this in a header, but it needs its own section; SKIP
        link1='info:org#External links' #info node or index link  USEFUL 
        link1='shell:ls *.org' #a shell command; anything with a space has to be in brackets to be a link 
        link1List.append(link1)
        link1='elist:org-agenda' #interactive Elisp command; must have brackets
        link1List.append(link1)
        link1='elisp:(find-file-other-frame "Elisp.org")' #Elisp form to evaluate; must have brackets 
        link1List.append(link1)
        link1='./*.org'  #asterisk wildcard in filename works in emacs
        link1List.append(link1)
        link1='file:./*.org'
        link1List.append(link1)
        link1='./*.py'
        link1List.append(link1)
        link1='file:./*.py'
        link1List.append(link1)

        for link1 in link1List:
            matchingRegex,matchObj,matchingClass=OFL.find_best_regex_match_for_text(link1)
            self.failIf(matchingRegex)

    #TODO left off at get_external_link_examples_part_5 in regexForVariousLinksInOrgMode1.py
#head do not see a test for make_regex_dict
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
