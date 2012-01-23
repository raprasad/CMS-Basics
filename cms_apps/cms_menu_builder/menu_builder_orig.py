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

class NodeProcessor:
    """Purpose: To build navigation where each Node has appropriate subclass attached.
    Trying to do this with fewer queries than a reverse lookup for --each-- node

    Instead, pull each subclass type based on the node ids in the queryset
    """
    @staticmethod
    def add_node_subclasses(node_qs, active_path_ids=[]):
        if node_qs is None:
            return node_qs

        # retrieve node subclass names.  e.g.: "Page", "PageDirect", "PageCustomView", etc
        subclass_dict = {}  # { subclass name : 1 }
        map(lambda x: subclass_dict.update({x.subclass_name:1}), node_qs)

        # retrieve node ids
        node_ids = map(lambda x: x.id, node_qs)

        # build a lookup of Node subclass instances { node_id : instance of subclass }; 
        #   e.g. { 31: <Page: yellow>, 32: <Page: banana>,29: <PageDirect: www.google.com>, 30: <Page: cherry>}
        #
        node_subclass_objects = {}  
        for subclass_name in subclass_dict.keys():  # iterate through node subclass names

            if (not subclass_name) or subclass_name == '':
                continue    # go to the next subclass name
            page_obj_type = eval(subclass_name)     # e.g. eval('Page')
            # retrieve subclass instances
            subclass_object_qs = page_obj_type.objects.select_related().filter(id__in=node_ids, visible=True) 
            # put subclass instances into lookup
            for subclass_obj in subclass_object_qs:  
                    node_subclass_objects.update({ subclass_obj.id: subclass_obj })

        # Iterate through the nodes and, if subclass available, REPLACE with the appropriate 'subclass'
        #
        formatted_nodes = []
        for nd in node_qs:
            # if subclass is available, replace the node with its subclass
            #formatted_nodes.append(node_subclass_objects.get(nd.id, nd))
            subclass_obj = node_subclass_objects.get(nd.id, None)
            if subclass_obj:
                formatted_node = subclass_obj
            else:
                formatted_node = nd
            
            if formatted_node.id in active_path_ids:
                formatted_node.active_path = True
            else:
                formatted_node.active_path = False
                
            formatted_nodes.append(nd)              # subclass not found, use the Node
                
        return formatted_nodes
    

class MenuBuilder:
    """Used to build various menus and add attributes such as 'active_path' 
    
    scenario: no selected_node, return L2 items (and L1 if include_root_node)
        attributes to set for visible nodes
        has_descendants (not needed)
    """
    def __init__(self, **kwargs):
        self.selected_node = kwargs.get('selected_node', None)  
        self.include_root_node = kwargs.get('include_root_node', False)
        self.breadcrumb_exclude_selected_node = kwargs.get('breadcrumb_exclude_selected_node', False)
        self.breadcrumb_nodes = []
        self.active_path_ids = []
        self.menu_items = []
        self.build_the_menu()
    
    def get_num_menu_items(self):
        if self.menu_items is None:
            return 0
        return len(self.menu_items)
    
    def show_breadcrumb_items(self):
        if self.breadcrumb_nodes is None or len(self.breadcrumb_nodes):
            print 'no breadcrumb nodes'
            return
            
        for n in self.breadcrumb_nodes:
            print '(%s) %s [id:%s] [vis:%s] [lft:%s] [rt:%s] [is root: %s]' % (cnt_str, n.breadcrumb(), n.id, n.visible, n.left_val,  n.right_val, n.is_root)
        
    def show_menu_items(self):
        if self.get_num_menu_items() == 0:
            print 'no menu items'

        for mi in self.get_menu_items():
            print '%s %s (%s)(active:%s)' % ('--' * mi.menu_level,  mi, mi.menu_level, mi.active_path)

    def get_menu_items(self):
        return self.menu_items
    
    def build_the_menu(self):
        # step 1: build the breadcrumb trail, also sets active_path_ids
        self.make_breadcrumb()
        
        # step 2: get the menu items!
        
        # 2a: get L2 menu items
        l2_menu_items = self.get_menu_by_level(2, self.include_root_node)
        if l2_menu_items is None:
            return None
                    
        # 2b: no 'selected_node', return the l2_menu_items
        if self.selected_node is None or self.active_path_ids in (None, [],):
            return NodeProcessor.add_node_subclasses(l2_menu_items, self.active_path_ids)
    
        # 2c: get the submenu items related to the 'selected_node':
        #           parents, siblings, and descendants 1 level down
        if len(self.active_path_ids) < 2:
            return NodeProcessor.add_node_subclasses(l2_menu_items, self.active_path_ids)
            
        l2_active_path_node_id = self.active_path_ids[1]
        
        # returns None or a queryset
        sub_menu_items = self.get_left_menu_nodes(self.selected_node, l2_active_path_node_id) 
        if sub_menu_items is None or sub_menu_items.count()==0:      # nothing found, return the l2 items
            return NodeProcessor.add_node_subclasses(l2_menu_items, self.active_path_ids)

        # at the L2 level, insert the sub_menu_items
        all_menu_items = []
        for idx, mi in enumerate(l2_menu_items):
            if mi.id == sub_menu_items[0].id:        # check above that sub_menu_items.count() is > 0
                all_menu_items += sub_menu_items    
            else:
                all_menu_items.append(mi)
        
        self.menu_items = NodeProcessor.add_node_subclasses(all_menu_items, self.active_path_ids)
    
    def get_menu_by_level(self, level=2, include_root_node=False):
        """Retrieve the menu for any given depth.  
            root node - level 1
            parent is root - level 2
        etc."""
        if (level is None) or str(level).isdigit() is False: 
            return None

        qs1 = Node.objects.select_related('parent').filter(visible=True)

        if include_root_node:
            qs2 = qs1.filter(Q(menu_level=2) | Q(menu_level=1)).order_by('left_val', 'sibling_order')
        else:
            qs2 = qs1.filter(menu_level=2).order_by('left_val', 'sibling_order')
        
        return qs2
        
    def get_left_menu_nodes(self, selected_node, l2_active_path_node_id):
        """Given a selected node, retrieve the nodes needed to create a left menu

            # Nodes for left menu display include
            # (1) Nodes where:
                    selected_node.menu_level > 1
                    selected_node.menu_level <= menu level/depth 
            # (2) Nodes where the "selected_node" is the parent

        """
        if selected_node is None or l2_active_path_node_id is None:
            return None
        
        try:
            level2_of_active_path = Node.objects.get(id=l2_active_path_node_id, visible=True)
        except Node.DoesNotExist:
            return None
        
        # Show at least the 3rd menu level, more if node selected is fourth or more
        menu_level_to_check = max(3, selected_node.menu_level)

        # Query the following:
        #   fyi: menu level, or level, refers to Node.menu_level attribute where 
        #           - Root is menu_level=1, 
        #           - Main Menu is menu_level=2, etc
        #
        # - Starting with main menu item, choose its tree, down to the menu level of the selected page
        #           - covers main menu to max(Level 3, selected_page Level)
        #
        # - Anything where parent is selected node (one step lower than initial part of query)
        #
        qs = Node.objects.filter(visible=True).filter( \
                Q(left_val__gt=level2_of_active_path.left_val,\
                    left_val__lt=level2_of_active_path.right_val,\
                    menu_level__lte=menu_level_to_check) |\
                    Q(parent=selected_node) \
                     ).order_by('left_val')
    
        return qs

    def make_breadcrumb(self):
        self.breadcrumb_nodes = self.get_breadcrumb_nodes()
    
    
    def get_breadcrumb_nodes(self):
        """For a given node, retrieve the breadcrumb nodes.
         Ordered with the root appearing first

         To exclude the selected node, the last node in the breadcrumb trail,
         set breadcrumb_exclude_selected_node to True
        """
        selected_node = self.selected_node
        if selected_node is None:
            return None

        if self.breadcrumb_exclude_selected_node:       
            # lt / gt - exclude selected_node
            qs = Node.objects.filter(visible=True\
                                    , left_val__lt=selected_node.left_val\
                                    , right_val__gt=selected_node.right_val).order_by('left_val')
        else:                       
            # lte / gte - include selected_node
            qs = Node.objects.filter(visible=True\
                                    , left_val__lte=selected_node.left_val\
                                    , right_val__gte=selected_node.right_val).order_by('left_val')

        self.active_path_ids = map(lambda x: x.id, qs)      # pull the active path ids for later use
        return NodeProcessor.add_node_subclasses(qs)  

       
        
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

def get_left_menu_nodes(selected_node, l2_node_on_active_path):
    """Given a selected node, retrieve the nodes needed to create a left menu
    
        # Nodes for left menu display include
        # (1) Nodes where:
                selected_node.menu_level > 1
                selected_node.menu_level <= menu level/depth 
        # (2) Nodes where the "selected_node" is the parent
        
    """
    if selected_node is None:
        return None
    
    # Left menu is everything under L2 of the active path
    if len(active_path_nodes) < 2:
        return
    
    level2_of_active_path = active_path_nodes[1]

    # Show at least the 3rd menu level, more if node selected is fourth or more
    menu_level_to_check = max(3, selected_node.menu_level)
    
    # Query the following:
    #   fyi: menu level, or level, refers to Node.menu_level attribute where 
    #           - Root is menu_level=1, 
    #           - Main Menu is menu_level=2, etc
    #
    # - Starting with main menu item, choose its tree, down to the menu level of the selected page
    #           - covers main menu to max(Level 3, selected_page Level)
    #
    # - Anything where parent is selected node (one step lower than initial part of query)
    #
    qs = Node.objects.filter(visible=True).filter( \
            Q(left_val__gt=level2_of_active_path.left_val,\
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
    
    
def get_main_menu(with_children=True, with_root_node=True):
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

    if with_root_node:
        fmt_lst = get_menu_by_level(1)
    else:
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
