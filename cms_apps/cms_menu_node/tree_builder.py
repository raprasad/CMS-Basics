from cms_common.msg_util import *
from django.db.models.signals import pre_save, post_save, post_delete     
#from cms_menu_node.models import Node


def rebuild_tree_after_node_saved(sender, **kwargs):
    """Rebuild the tree each time a Node is saved.
    This includes:
        - making sure a root exists
        - setting the left_val/right_val for Modified Preorder Tree Traversal (MPTT)
        - resetting sibling orders based on relative MPTT vals
        - setting the node.menu_level val  (this is menu depth)
    - sender is a Node object"""    
    #msgt('kwargs: %s' % kwargs)
    
    calling_node = kwargs.get('instance', None)    
    if not calling_node:
        return

    NODE_CLASS = get_to_node_class(sender)

    # to avoid infinite loop, disconnect the post-save signal
    #--------------------------
    disconnect_node_signals(NODE_CLASS)
    #--------------------------
        
    # get the root node -- assume there is only one!
    root_node = None
    try:
        root_node = NODE_CLASS.objects.get(is_root=True, visible=True)
    except NODE_CLASS.DoesNotExist:
        # No root node or more than one - Fix it!
        #msg('Root does not Exist!')
        check_for_single_root(calling_node)
    except NODE_CLASS.MultipleObjectsReturned:
        check_for_single_root(calling_node)
    
    if root_node is None:
        try:
            root_node = NODE_CLASS.objects.get(is_root=True, visible=True)
        except NODE_CLASS.DoesNotExist:
            connect_node_signals(NODE_CLASS)
            #msg('Root Fix failed!')
            return


    # (1) rebuild the left/right values
    rebuild_tree(root_node)
    
    # (2) set the menu level attribute (menu depth) and the sibling order
    for n in NODE_CLASS.objects.all():
        n.set_menu_level()
        n.sibling_order = n.left_val
        n.save()
    
    
    # re-connect the post-save signal
    #--------------------------
    connect_node_signals(NODE_CLASS)
    #--------------------------
    
    
    
def rebuild_tree(parent_node, left_val=1):
    """Recursive function to rebuild right/left tree values based on parent relationships.
    Purpose is to create a Modified Preorder Tree Traversal (MPTT)
    Modified from PHP example here: http://blogs.sitepoint.com/hierarchical-data-database-2/
        To run: rebuild_tree(root_node)
    """
    if parent_node is None:
        return
    
    NODE_CLASS = parent_node.__class__
       
    #msg('rebuild tree: [%s][%s]' % (parent_node, left_val))
    right_val = left_val + 1
    
    # get children of this node
    for child_node in NODE_CLASS.objects.filter(parent=parent_node, visible=True).order_by('sibling_order'):
        # for each child of this node "right_val" is the current right value,
        # which is incremented by the rebuild_tree function   
        right_val = rebuild_tree(child_node, right_val)

    # we've got the left value, and now that we've processed   
    # the children of this node we also know the right value   
    parent_node.left_val = left_val
    parent_node.right_val = right_val
    parent_node.save()
    
    return right_val + 1
    

def rebuild_tree_after_node_deleted(sender, **kwargs):
    """Called after node deletion.  In most cases, rebuild the tree after deletion.

    But there is an exception if it's the last visible node being deleted
    """
    node_to_delete = kwargs.get('instance', None)    
    if not node_to_delete:
        return

    NODE_CLASS =sender
    """
    Is this the last visible noded being deleted?  Then don't rebuild the tree
    """
    if NODE_CLASS.objects.filter(visible=True).exclude(pk=node_to_delete.id).count()==0:
        """We're doing this to prevent the 'deleted node' from being saved again
        (1) rebuild_tree being saved
        (2) calling "check_for_single_root"
        (3) In check_for_single_root, if a node doesn't have an id, then save() is called on the supposedly deleted node
        
        .exclude clause shouldn't be needed in query
        """
        return

    rebuild_tree_after_node_saved(sender, **kwargs)


def check_for_single_root(node_to_be_saved):            #sender=None, **kwargs):
    """There should always be 1 and only 1 root node.
    Check for this each time a Node object is saved

    NTS = Node to Save

    possibilities:
    (1) node_to_be_saved is the only visible node -> make it the root  (May be first Node added to system)
    (2) more than one root node
    (3) new root?
    
    (4) root has been deleted
    """    
    if node_to_be_saved is None:
        return
        
    NODE_CLASS = node_to_be_saved.__class__
    
    #msgt('node_to_be_saved: [obj:%s] [name:%s]' % ( node_to_be_saved, node_to_be_saved.name))
    #msg('id: %s' % node_to_be_saved.id)

    # If it doesn't have one, give the node to be saved an id
    if node_to_be_saved.id is None:
        node_to_be_saved.save()         # save it so that it can be parent of old root
        
    # check (1)
    #
    #msg('(1) Only visible node -> make it the root')
    if node_to_be_saved and NODE_CLASS.objects.filter(visible=True).exclude(pk=node_to_be_saved.id).count() == 0:    
        node_to_be_saved.parent = None
        node_to_be_saved.visible = True # make sure it is visible
        node_to_be_saved.save()
        #msg('ok')
        return

    #msg('(2) Multiple root nodes  (multiple nodes with no parent)')
    #
    root_nodes = NODE_CLASS.objects.filter(parent=None, visible=True).order_by('left_val', 'sibling_order')
    if root_nodes.count() > 1:
        #   Make the 1st node the root and the rest its children
        new_root_node = None
        for idx, rn in enumerate(root_nodes):
            if idx==0:
                new_root_node = rn
            else:
                rn.parent = new_root_node
                rn.parent.is_root = False
                rn.save()
        #msg('ok')
        return
        
            
    #
    #
    #msg('(3) node_to_be_saved is not a root node, there is already 1 root node')
    if node_to_be_saved and node_to_be_saved.parent is not None and NODE_CLASS.objects.filter(is_root=True, visible=True).exclude(pk=node_to_be_saved.id).count() ==1:
        #msg('ok')
        return


    #msg('(4) node_to_be_saved is a new root node, make the NTS parent of current root')
    if node_to_be_saved and node_to_be_saved.parent is None and NODE_CLASS.objects.filter(visible=True).count() > 1:
        #msg('-> yes')
        node_to_be_saved.visible = True # make sure it is visible
        node_to_be_saved.save()         # check This!
        
        for rn in NODE_CLASS.objects.filter(parent=None, visible=True).exclude(pk=node_to_be_saved.id):
            if rn.id == node_to_be_saved.id or rn == node_to_be_saved:     # this is the new root, skip it
                pass
            else:
                rn.parent = node_to_be_saved    # set new parent for old root
                rn.save()
        return
        
    #msg('(5) There are no root nodes! Make a new root node by following the parent of current node')
    if node_to_be_saved is None:
        visible_nodes = NODE_CLASS.objects.filter(visible=True).order_by('left_val', 'sibling_order')
        if visible_nodes.count() > 0:
            not_to_be_saved = visible_nodes[0]
        else:
            return 
            
    potential_root = node_to_be_saved
    level_cnt = 0
    while potential_root.parent is not None:          
        level_cnt +=1
        potential_root = potential_root.parent        # iterate to top of tree for this node
        if level_cnt == 100: break              # something seriously wrong
    potential_root.visible=True
    potential_root.save()
    

def get_to_node_class(sender):
    if sender is None:
        # log a critical err
        msgx('FAIL:  NODE_CLASS is None')
        
    # get to the Node class
    NODE_CLASS_NAME = 'Node'
    if sender.__name__ == NODE_CLASS_NAME:
        return sender
    
    # only checking depth of one level
    for bc in sender.__bases__: 
        if bc.__name__ == NODE_CLASS_NAME:
            return bc
                
    # log a critical err
    msgx('FAIL:  NODE_CLASS is None')


def disconnect_node_signals(node_obj_class):
    node_obj_class = get_to_node_class(node_obj_class)  # in case sender is a child of Node
    """For Node: disconnect the post-save and pre-save signals"""
    #pre_save.disconnect(check_for_single_root, sender=Node)    
    post_save.disconnect(rebuild_tree_after_node_saved, sender=node_obj_class)    
    post_delete.disconnect(rebuild_tree_after_node_deleted, sender=node_obj_class)    

def connect_node_signals(node_obj_class):
    node_obj_class = get_to_node_class(node_obj_class)  # in case sender is a child of Node
    """For Node: re-connect the post-save and pre-save signals"""
    #pre_save.connect(check_for_single_root, sender=Node)    
    post_save.connect(rebuild_tree_after_node_saved, sender=node_obj_class)    
    post_delete.connect(rebuild_tree_after_node_deleted, sender=node_obj_class)    
