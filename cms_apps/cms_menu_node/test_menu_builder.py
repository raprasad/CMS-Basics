import unittest
from django.test import TestCase
import time
from cms_common.msg_util import *
from cms_menu_node.models import Node, BREADCRUMB_SEPARATOR, STR_NOT_VISIBLE
from cms_menu_builder.menu_builder import *
#from cms_menu_node.test_menu_builder import *
from test_mptt_tree import get_node, show_loaded_nodes
        
class MenuBuilderTest(TestCase):
    fixtures = ['cms_menu_node_test_data.json']
    """
    -food (L1)
        - fruit (L2)
            - red    
                - cherry
            - yellow    
                - banana
            - tropical  
                - papaya
                - pinepple
            - local       
                - apple
        - meat (L2)
            - beef
            - pork
        - vegetable (L2)
            - root
                - potato
                - yam
                - yucca
            - nightshade
                - tomato
                - eggplant
    """
    def setUp(self):
        pass
        
    def runTest(self):
        show_loaded_nodes()
        #--------------------------------------------
        msgt('Should be 22 test nodes, actual count: [%s]' % Node.objects.all().count())
        self.assertEqual(Node.objects.all().count(), 22)

        #-------------------------------------------------------
        papaya = get_node(name='papaya')
        menu_builder = MenuBuilder(selected_node=papaya, include_root_node=True)
        msgt('retrieve menu for papaya, should be 13 menu items, actual: [%s]' % menu_builder.get_num_menu_items())
        self.assertEqual(menu_builder.get_num_menu_items(), 13)
        
        active_items = filter(lambda x: x.active_path, menu_builder.get_menu_items())
        msgt('menu for papaya: 4/13 items are active, actual: [%s]' % len(active_items))
        self.assertEqual(len(active_items), 4)
        
        print 'breadcrumb from mbuilder: '
        menu_builder.show_breadcrumb_items()
        msgt('bc from node: %s' % papaya.breadcrumb())
        
        menu_builder.show_menu_items()

        #-------------------------------------------------------
        msgt('retrieve menu for tropical, should be 10 menu items')        
        tropical = get_node(name='tropical')
        menu_builder = MenuBuilder(selected_node=tropical, include_root_node=True)
        menu_builder.show_menu_items()
        msg('actual: [%s]' % menu_builder.get_num_menu_items())
        self.assertEqual(menu_builder.get_num_menu_items(), 10)
        
        msgt('check number of breadcrumb items, should be 3')
        menu_builder.show_breadcrumb_items()
        self.assertEqual(menu_builder.get_num_breadcrumbs(), 3)
        msg('actual: [%s]' % menu_builder.get_num_breadcrumbs())

        #-------------------------------------------------------
        msgt('tropical selected, but excluded from breadcrumb')
        menu_builder = MenuBuilder(selected_node=tropical, include_root_node=True, breadcrumb_exclude_selected_node=True)
        menu_builder.show_menu_items()
        
        msgt('check number of breadcrumb items, should be 2')
        menu_builder.show_breadcrumb_items()
        self.assertEqual(menu_builder.get_num_breadcrumbs(), 2)
        msg('actual: [%s]' % menu_builder.get_num_breadcrumbs())
        
        #-------------------------------------------------------
        msgt("make sure 'tropical' is an active menu item")
        tropical_active = False
        for mi in menu_builder.get_menu_items():
            if tropical.id == mi.id and mi.active_path:
                tropical_active=True
        self.assertEqual(tropical_active, True)
        msg('yup')
        
        #-------------------------------------------------------
        msgt('No selected node, exclude root_node, should be 3 menu items')
        menu_builder = MenuBuilder(include_root_node=False)
        menu_builder.show_menu_items()
        msg('actual: [%s]' % menu_builder.get_num_menu_items())
        self.assertEqual(menu_builder.get_num_menu_items(), 3)

        msgt("... check that they're all L2 items")
        l2_menu_items = filter(lambda x: x.menu_level==2, menu_builder.get_menu_items())
        self.assertEqual(len(l2_menu_items), 3)
        
        #-------------------------------------------------------
        msgt('No selected node, should be 4 menu items')
        menu_builder = MenuBuilder()
        menu_builder.show_menu_items()
        msg('actual: [%s]' % menu_builder.get_num_menu_items())
        self.assertEqual(menu_builder.get_num_menu_items(), 4)
                
        #-------------------------------------------------------        
        msgt('delete tropical, siblings should be: red|yellow|papaya|pineapple|local')
        tropical.delete()
        local = get_node(name='local')
        menu_builder = MenuBuilder(selected_node=local)
        menu_builder.show_menu_items()
        l3_items = active_items = filter(lambda x: x.menu_level==3, menu_builder.get_menu_items())
        self.assertEqual(len(l3_items), 5)
        self.assertEqual(menu_builder.get_num_menu_items(), 10)
        #--------------------------------------------
                
        msgt('delete everything but the root, should only be 1 menu item')
        Node.objects.filter(menu_level__gte=2).delete() # delete everything but the root
        menu_builder = MenuBuilder(include_root_node=True)
        self.assertEqual(menu_builder.get_num_menu_items(), 1)
        menu_builder.show_menu_items()
        
        