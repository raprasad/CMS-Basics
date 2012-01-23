import unittest
from test_mptt_tree import TreeRearrangement, NodeTestCase      
from test_menu_builder import MenuBuilderTest

def suite():
    suite = unittest.TestSuite()
    #suite.addTest(TreeRearrangement('runTest'))
    #suite.addTest(NodeTestCase('test_root'))
    suite.addTest(MenuBuilderTest('runTest'))
    return suite        
