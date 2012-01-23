import unittest
from django.test import TestCase
import time
from cms_common.msg_util import *
from cms_menu_node.models import Node, BREADCRUMB_SEPARATOR, STR_NOT_VISIBLE
from cms_menu_node.exceptions import ParentRelationshipCircular

def get_node(name):
    try:
        return Node.objects.get(name=name)
    except Node.DoesNotExist:
        dashes()
        msg('error')
        msgx('Failed to find node: %s' % name)
        
def show_loaded_nodes():
    msgt('nodes loaded:')
    cnt =0
    for n in Node.objects.all().order_by('left_val', 'right_val'):
        cnt +=1
        if cnt < 10: cnt_str = '0%s' % cnt
        else: cnt_str = cnt
        print '(%s) %s [id:%s] [vis:%s] [lft:%s] [rt:%s] [is root: %s]' % (cnt_str, n.breadcrumb(), n.id, n.visible, n.left_val,  n.right_val, n.is_root)


        
class TreeRearrangement(TestCase):
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
        msgt('Should be 22 test nodes')
        self.assertEqual(Node.objects.all().count(), 22)
        msg('ok')
        
        #--------------------------------------------
        msgt('Hide Vegetable node--its children should not be visible in the breadcrumb')
        node_to_hide = Node.objects.get(name='vegetable')
        node_to_hide.visible=False
        node_to_hide.save()
        show_loaded_nodes()
        
        # This node and it's children should not be visible (visible not set, but appears in breadcrumb)
        for child_node in Node.objects.filter(left_val__gt=node_to_hide.left_val \
                                            ,right_val__lt=node_to_hide.left_val):
            self.assertGreaterEqual(child_node.breadcrumb.find(STR_NOT_VISIBLE), 0)
        msg('ok')
        
        #--------------------------------------------
        msgt('Make vegetable node visible again, children should also be visible in breadcrumb')
        node_to_hide.visible=True
        node_to_hide.save()
        for child_node in Node.objects.filter(left_val__gt=node_to_hide.left_val \
                                            ,right_val__lt=node_to_hide.left_val):
            self.assertEqual(child_node.breadcrumb.find(STR_NOT_VISIBLE), -1)
        msg('ok')
        
        
        #--------------------------------------------
        msgt('Delete "yellow" node.  Its child, "banana" should now have the parent "fruit"')
        Node.objects.get(name='yellow').delete()
        banana_node = get_node('banana')
        self.assertEqual(banana_node.parent.name, 'fruit')
        msg('ok')
        
        #--------------------------------------------
        msgt('Add "kiwi" as a "tropical" fruit')
        Node.objects.create(name='kiwi'\
                        , parent=get_node('tropical'))
        kiwi = Node.objects.get(name='kiwi')
        sep = ' %s ' % BREADCRUMB_SEPARATOR
        self.assertEqual(kiwi.breadcrumb(), sep.join("""food fruit tropical kiwi""".split()))
        print kiwi.breadcrumb()
        msg('ok')
        #show_loaded_nodes()

        #--------------------------------------------
        msgt('put "kiwi" after siblings: "papaya" and "pineapple"')
        kiwi.sibling_order= 999
        kiwi.save()
        self.assertEqual(get_node('kiwi').left_val > get_node('papaya').left_val, True )
        self.assertEqual(get_node('kiwi').left_val > get_node('pineapple').left_val, True )
        msg('ok')

        #--------------------------------------------
        msgt('Try to create circular relationship and raise error')
        # food -> vegetable -> root -> yam
        yam = get_node('yam')
        veg = get_node('vegetable')
        veg.parent = yam
        try:
            veg.save()
        except ParentRelationshipCircular as e:
            print str(e)
            self.assertEquals(str(e), str(ParentRelationshipCircular(veg)) )
        msg('ok')
        
        show_loaded_nodes()
        
        #--------------------------------------------
        msgt('Add a new root')
        things = Node(name='things (new root)', parent=None)
        things.save()
        self.assertEquals(Node.objects.filter(is_root=True, visible=True ).count(), 1)
        self.assertEquals(get_node('things (new root)').left_val, 1)
        msg('ok')

        #--------------------------------------------
        msgt('Is old root a child of the new root?')
        self.assertEquals(get_node('food').parent, things)
        msg('ok')
        show_loaded_nodes()

        #--------------------------------------------
        msgt('delete new root: "food" should be replacement root')
        get_node('things (new root)').delete()   # new root deleted
        food = get_node('food')
        self.assertEquals(food.left_val, 1)
        self.assertEquals(food.is_root, True)
        self.assertEquals(food.visible, True)
        msg('ok')

        show_loaded_nodes()
        
        #--------------------------------------------
        msgt('Make root visible=False -> should fail, reverting back to visible=True')
        food = get_node('food')
        food.visible=False
        food.save()
        self.assertEquals(get_node('food').visible, True)
        msg('ok')

        #--------------------------------------------
        msgt("delete root again.  'food' should be replaced by child 'fruit'")
        get_node('food').delete()
        fruit = get_node('fruit')
        self.assertEquals(fruit.left_val, 1)
        self.assertEquals(fruit.is_root, True)
        self.assertEquals(fruit.visible, True)
        msg('ok')
        msg("tree is messed up, but there's still a root:)")
        show_loaded_nodes()
        
        
class NodeTestCase(TestCase):
    def setUp(self):
        msgt('setup: create root node')
        self.root_node_name = 'THE ROOT'
        self.node1 = Node.objects.create(name=self.root_node_name\
                                    , visible=True\
                                    , parent=None)

        show_loaded_nodes()
    def show_loaded_nodes(self):
        msgt('nodes loaded:')
        cnt =0
        for n in Node.objects.all().order_by('left_val', 'right_val'):
            cnt +=1
            if cnt < 10: cnt_str = '0%s' % cnt
            else: cnt_str = cnt
            print '(%s) %s [id:%s] [vis:%s] [lft:%s]' % (cnt_str, n.breadcrumb(), n.id, n.visible, n.left_val)
        
  
    def test_root(self):
        msgt('running test_root')
        msg('> retrieve root from db (if not, vals don\'t show correctly)')
            
        self.node1 = get_node(self.root_node_name)
        self.assertEqual(self.node1.name, self.root_node_name)
                
        #msg('sleep 2 seconds')
        #time.sleep(2)
        self.node1.show()
        msg('> only one node exists')

        msgt('node count: %s' % Node.objects.all().count())
        self.assertEqual(Node.objects.all().count(), 1)
        msg('ok')

        msgt('"is_root" is set correctly?')
        self.assertEqual(self.node1.is_root, True)
        msg('ok')
        
        msgt('create "Faculty" node')
        node2_name = 'Faculty'
        self.node2 = Node.objects.create(name=node2_name, parent=self.node1)
        #show_loaded_nodes()

        msgt('check breadcrumbs')
        self.node1 = get_node(self.root_node_name)
        self.assertEqual(get_node(self.root_node_name).breadcrumb(), self.root_node_name)
        self.assertEqual(get_node(node2_name).breadcrumb(), '%s %s %s' % (self.root_node_name, BREADCRUMB_SEPARATOR, node2_name ) )
        msg('breadcrumbs good')
        
        msgt('check # descendants')
        msg('node 1 descendant count: %s' % self.node1.get_num_descendants())
        self.assertEqual(self.node1.get_num_descendants(), 1)
        msg('ok')
        
        msgt('is menu level correct?')
        self.assertEqual(self.node1.menu_level, 1)
        msg('ok')
        
        show_loaded_nodes()
        
        msgt("""Make two roots by setting:
        faculty_root.parent = None
On save, a correction should restore the previous root""")
        faculty_root = get_node(node2_name)
        faculty_root.parent = None
        faculty_root.save()
        
        show_loaded_nodes()
        
        self.assertEquals(get_node(self.root_node_name).is_root, True)
        self.assertEquals(get_node(node2_name).parent, get_node(self.root_node_name))
        self.assertEquals(get_node(node2_name).is_root, False)
        self.assertEquals(get_node(node2_name).left_val, get_node(self.root_node_name).left_val+1)

        show_loaded_nodes()
        
        msgt("""Delete the root, faculty should be the new root""")
        get_node(self.root_node_name).delete()
        self.assertEquals(get_node(node2_name).parent, None)
        self.assertEquals(get_node(node2_name).is_root, True)
        self.assertEquals(get_node(node2_name).left_val, 1)
        show_loaded_nodes()
        
        msgt('Delete the last node')
        n2 = get_node(node2_name)
        n2.delete()
        self.assertEquals(Node.objects.all().count(), 0)
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(BuildMenuTest('runTest'))
    #suite.addTest(TreeRearrangement('runTest'))
    #suite.addTest(NodeTestCase('test_root'))
    return suite        
