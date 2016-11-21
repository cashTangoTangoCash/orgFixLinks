import unittest
import orgFixLinks as OFL

#TODO test regexOrderedList, or part of larger test?
#TODO test regexDict, or part of larger test?
#TODO test OrgFile.myUniqueIDRegex, or part of larger test?

#TODO merge this with previous test file?  no, that file seems too specialized

#TODO test that unique ID generator makes unique IDs that are detected by appropriate regex

#TODO test converting a line into list of objects, than back into the same line (catch bug that is adding spaces)

#TODO test find_unique_id_inside_org_file: need test org files that do and do not contain unique ID

#TODO could use some test files also used by AutomaticTests1.py

class TestGetAsteriskLevel(unittest.TestCase):
    def testGetAsteriskLevel(self):
        '''test get_asterisk_level'''
        line='* junk text\n'
        self.assertEqual(OFL.get_asterisk_level(line),1)
        
        line='*** junk text\n'
        self.assertEqual(OFL.get_asterisk_level(line),3)

        line='junk text\n'
        self.assertEqual(OFL.get_asterisk_level(line),0)

        line='junk *** text ***\n'
        self.assertEqual(OFL.get_asterisk_level(line),0)

class TestNodeFunctions(unittest.TestCase):
    def testFindUniqueID1(self):
        '''test Node.findUniqueID with uniqueIDRegexObj set to OrgFile.myUniqueIDRegex'''

        testLines1=['* status\n','#MyUniqueID2016-05-19_17-15-59-9812   \n']
        node1=OFL.Node(testLines1,sourceFile=None)
        node1.findUniqueID(OFL.OrgFile.myUniqueIDRegex)
        self.failUnless(node1.uniqueID)
        self.assertEqual(node1.uniqueID,'2016-05-19_17-15-59-9812')

    def testFindUniqueID2(self):
        '''test Node.findUniqueID with uniqueIDRegexObj set to OrgFile.myUniqueIDRegex'''

        testLines1=['* status\n','** #MyUniqueID2016-05-19_17-15-59-9812   \n']
        node1=OFL.Node(testLines1,sourceFile=None)
        node1.findUniqueID(OFL.OrgFile.myUniqueIDRegex)
        self.failIf(node1.uniqueID)

#head
if __name__ == "__main__":
    unittest.main()
