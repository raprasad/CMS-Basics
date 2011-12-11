"""
Depends on: 
    - cms_common
    - cms_menu_node
    - cms_page
    
Purpose: To build navigation where each Node is replaced by the appropriate subclass.
         Trying to do this with fewer queries than a reverse lookup for --each-- node
         
         Want to be able to do the following in a template w/o a reverse lookup:
    
            > node_obj.get_absolute_url
                - where the node_obj could be a Node, Page, PageDirectLink, etc
"""
from django.db.models import Q
from cms_common.msg_util import *
from cms_menu_node.models import Node
from cms_page.models import *


def build_menu(node_qs):
    """Purpose: To build navigation where each Node has appropriate subclass attached.
    Trying to do this with fewer queries than a reverse lookup for --each-- node
    
    Instead, pull each subclass type based on the node ids in the queryset

from cms_menu_node.models import Node
qs= Node.objects.all()
    """
    if node_qs is None:
        return node_qs
        
    #qs= Node.objects.all()
    #node_qs.order_by('left_val', 'right_val')

    # retrieve node subclass names.  e.g.: "Page", "PageDirect", "PageCustomView", etc
    subclass_dict = {}
    map(lambda x: subclass_dict.update({x.subclass_name:1}), node_qs)

    #msg('subclass_dict: %s' % subclass_dict)
    # retrieve Node ids
    node_ids = map(lambda x: x.id, node_qs)

    # build a lookup of Node subclass instances { node_id : instance of subclass }; 
    #   e.g. { 31: <Page: yellow>, 32: <Page: banana>,29: <PageDirect: www.google.com>, 30: <Page: cherry>}
    #
    node_subclass_objects = {}
    for subclass_name in subclass_dict.keys():  # iterate through node subclass names

        if subclass_name and not subclass_name == '':
            page_obj_type = eval(subclass_name)     # e.g. eval('Page')
            subclass_object_qs = page_obj_type.objects.select_related().filter(id__in=node_ids, visible=True) # retrieve subclass instances

            for subclass_obj in subclass_object_qs:  # put subclass instances into lookup
                node_subclass_objects.update({ subclass_obj.id: subclass_obj })
    
    # Iterate through the nodes and, when available, REPLACE with the appropriate 'subclass'
    #
    formatted_nodes = []
    for fn in node_qs:
        subclass_obj = node_subclass_objects.get(fn.id, None)

        #print '\n %s: %s' % (fn, subclass_obj.__class__.__name__)
        #print 'get_absolute_url: %s' %  subclass_obj.get_absolute_url()
        if subclass_obj:
            formatted_nodes.append(subclass_obj)
        else:
            formatted_nodes.append(fn)
    return formatted_nodes


def set_active_path_attribute(node, active_path_ids):
    """Given a node and a [] of active_path_ids, 
    add an "active_path" attribute to the node with a True/False val
    """
    if active_path_ids is None:
        return node
     
    if node.id in active_path_ids:
        #print 'YES active path', node, node.id
        node.active_path = True
    else:
        #print 'NO active path', node, node.id
        node.active_path = False       
    
    return node

def get_left_menu_nodes(selected_node, active_path_nodes=None):
    """Given a selected node, retrieve the nodes needed to create a left menu
    
        # Nodes for left menu display include
        # (1) Nodes with a  1 < selected_node.menu_level <= menu level/depth 
        # (2) Nodes where the "selected_node" is the parent
        
    """
    if selected_node is None:
        return None
    #msg('get_left_menu_nodes')
    #msg('active path nodes: %s' % active_path_nodes)
    
    # Left menu is everything under L2 of the active path
    if len(active_path_nodes) < 2:
        return
    
    level2_of_active_path = active_path_nodes[1]
    #qs = Node.objects.filter(visible=True).filter(menu_level__gt=2).filter(Q(menu_level__lte=selected_node.menu_level, ) \
    #                                        |Q(parent=selected_node)).order_by('left_val')

    # Show at least the 3rd menu level, more if node selected is fourth or more
    menu_level_to_check = max(3, selected_node.menu_level)
    
    # Query the following:
    #   fyi: menu level, or level, refers to Node.menu_level attribute where Root is menu_level=1, Main Menu is menu_level=2, etc
    # - Starting with main menu item, choose its tree, down to the menu level of the selected page
    #           - covers main menu to max(Level 3, selected_page Level)
    #
    # - Anything where parent is selected node (one step lower than initial part of query
    #
    qs = Node.objects.filter(visible=True).filter( Q(left_val__gt=level2_of_active_path.left_val,\
                                                    left_val__lt=level2_of_active_path.right_val,\
                                                    menu_level__lte=menu_level_to_check) |\
                                                    Q(parent=selected_node) \
                                                     ).order_by('left_val')
                              #                     Q(left_val__gt=selected_node.left_val, \
                              #                      left_val__lt=selected_node.right_val ,
                              #                     menu_level__lte=menu_level_to_check) |\
    
    qs = build_menu(qs)
    
    if active_path_nodes:
        active_path_ids = map(lambda x: x.id, active_path_nodes)
        qs = map(lambda x: set_active_path_attribute(x, active_path_ids), qs)
            
    return qs
    
def get_menu_by_level(level=2):
    """Retrieve the menu for any given depth.  
    root node - level 1
    parent is root - level 2
    etc."""
    if level is None: return None
    if not str(level).isdigit(): return None
    
    qs = Node.objects.select_related('parent').filter(menu_level=level, visible=True).order_by('left_val', 'sibling_order')
    return build_menu(qs)
    
    
def get_main_menu(with_children=True):
    """Shortcut to retrieve main menu nodes.
    The main menu consists of:
        (1) visible Nodes at menu_level=2  (menu_level=1 is the root)
        (2) visible child nodes at menu_level=3
    """
    if not with_children:
        return get_menu_by_level(2)
    
    # Get the Main Menu nodes
    l2_nodes = get_menu_by_level(2)
    l2_ordered_ids = []     # array of ordered main menu ids
    l2_lookup = {}   
    for x in l2_nodes:
        x.child_nodes = []              # initiate array of child nodes
        l2_ordered_ids.append(x.id)
        l2_lookup.update({x.id : x})     # Make a dict of { Level 2 Node ID : Level 2 Node }
        
    l3_nodes = get_menu_by_level(3)
        
    # attach the children to the parents
    for l3_node in l3_nodes:
        #print '%s: %s %s' % (l3_node, l3_node.__class__.__name__, l3_node.get_absolute_url())
        
        #print l3_node.node_ptr_id
        l2_node = l2_lookup.get(l3_node.parent_id, None)    # find the parent
        if l2_node is not None:
            l2_node.child_nodes.append(l3_node)             # add the child node
            l2_lookup.update({ l2_node.id : l2_node })        # update the lookup
    #return l2_nodes

    fmt_lst = []

    for l2_id in l2_ordered_ids:
        fmt_lst.append(l2_lookup.get(l2_id))        # assume that all ids are in the list
    return fmt_lst
    
def get_breadcrumb_nodes(selected_node, exclude_selected_node=False):
    """For a given node, retrieve the breadcrumb nodes.
    Ordered with the root appearing first
    
    To exclude the selected node, the last node in the breadcrumb trail, set exclude_selected_node to True
    """
    if selected_node is None:
        return None

    if exclude_selected_node:       # lt / gt - exclude selected_node
        qs = Node.objects.filter(visible=True, left_val__lt=selected_node.left_val, right_val__gt=selected_node.right_val).order_by('left_val')
    else:                       # lte / gte - include selected_node
        qs = Node.objects.filter(visible=True, left_val__lte=selected_node.left_val, right_val__gte=selected_node.right_val).order_by('left_val')

    return build_menu(qs)

def get_breadcrumb_nodes_no_leaf(selected_node):
    """Shortcut to retrieve breadcrumb nodes without the selected node"""
    return get_breadcrumb_nodes(selected_node, exclude_selected_node=True)
