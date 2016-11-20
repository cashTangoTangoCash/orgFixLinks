import unittest
import orgFixLinks as OFL

#TODO test regexOrderedList
#TODO test regexDict

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

#head
if __name__ == "__main__":
    unittest.main()
