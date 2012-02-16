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
    
    Also, adds: "selected_node" and "active_path" attributes
    """
    @staticmethod
    def add_node_subclasses(node_qs, active_path_ids=[]):
    
        if node_qs is None:
            return node_qs

        if active_path_ids is None:
            active_path_ids = []
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
                # subclass not found, use the Node
                formatted_node = nd

            if formatted_node.id in active_path_ids:
                formatted_node.active_path = True
            else:
                formatted_node.active_path = False
                
            if len(active_path_ids) > 0 and nd.id == active_path_ids[-1]:
                formatted_node.selected_node = True
                
            formatted_nodes.append(formatted_node)      
        return formatted_nodes


class BreadcrumbHandler:
    def __init__(self, breadcrumbs, last_breadcrumb_string=None):
        self.breadcrumbs = breadcrumbs
        self.last_breadcrumb_string = last_breadcrumb_string
    
    def get_breadcrumbs(self):
        return self.breadcrumbs 
    
    def get_num_breadcrumbs(self):
        if self.breadcrumbs:
            return len(self.breadcrumbs)
        return 0
        
    def has_last_breadcrumb_string(self):
        if self.last_breadcrumb_string is None:
            return False
        return True
        
    def get_last_breadcrumb_string(self):
        if self.last_breadcrumb_string is None:
            return None        
        return str(self.last_breadcrumb_string)
        
        
class MenuBuilder:
    """Used to build various menus and add 'active_path' attribute
    kwargs:  
        selected_node   (default: None)
        include_root_node (default: True)
        breadcrumb_exclude_selected_node (default: False)
    """
    def __init__(self, **kwargs):
        self.selected_node = kwargs.get('selected_node', None)  
        self.include_root_node = kwargs.get('include_root_node', True)
        self.breadcrumb_exclude_selected_node = kwargs.get('breadcrumb_exclude_selected_node', False)
        self.breadcrumb_nodes = []
        self.last_breadcrumb_string = None
        
        self.active_path_ids = []
        self.menu_items = []
        self.build_the_menu()
    
    @staticmethod
    def get_default_menu_items():
        mb = MenuBuilder()
        return mb.get_menu_items()
    
    def get_breadcrumb_handler(self):
        return BreadcrumbHandler(self.breadcrumb_nodes, self.last_breadcrumb_string)
        
    def add_breadcrumb_item(self, bn):
        if bn is None or self.breadcrumb_nodes is None:
            return
        self.breadcrumb_nodes.append(bn)
        
    def set_last_breadcrumb_as_string(self, bn):
        if bn is None: return
        self.last_breadcrumb_string = str(bn)
        
    def get_breadcrumb_nodes(self):
        return self.breadcrumb_nodes
        
    def get_num_breadcrumbs(self):
        if self.breadcrumb_nodes is None:
            return 0
        return len(self.breadcrumb_nodes)

    def get_num_menu_items(self):
        if self.menu_items is None:
            return 0
        return len(self.menu_items)
    
    def show_breadcrumb_items(self):
        print '-' *40
        print 'show_breadcrumb_items'
        if self.breadcrumb_nodes is None:
            print 'no breadcrumb nodes'
            return
        cnt = 0
        for n in self.breadcrumb_nodes:
            cnt+=1
            print '(%s) %s [id:%s] [vis:%s] [lft:%s] [rt:%s] [is root: %s]' % (cnt, n.breadcrumb(), n.id, n.visible, n.left_val,  n.right_val, n.is_root)
        
    def show_menu_items(self):
        if self.get_num_menu_items() == 0:
            print 'no menu items'

        for mi in self.get_menu_items():
            print '%s (%s) %s (active:%s)' % ('-+-' * mi.menu_level,  mi.menu_level,mi,  mi.active_path)

    def get_menu_items(self):
        return self.menu_items
    
    def build_the_menu(self):
        # step 1: build the breadcrumb trail, also sets active_path_ids
        self.set_breadcrumb_nodes()
        
        # step 2: get the menu items!
        
        # 2a: get L2 menu items
        l2_menu_items = self.get_menu_by_level(2, self.include_root_node)
        
        if l2_menu_items is None:
            self.menu_items = NodeProcessor.add_node_subclasses(l2_menu_items, self.active_path_ids)
            return
            
        # 2b: no 'selected_node', menu_items are the l2_menu_items
        if self.selected_node is None or self.active_path_ids in (None, [],):
            self.menu_items =  NodeProcessor.add_node_subclasses(l2_menu_items, self.active_path_ids)
            return
            
        # 2c: get the submenu items related to the 'selected_node':
        #           parents, siblings, and descendants 1 level down
        if len(self.active_path_ids) < 2:
            self.menu_items = NodeProcessor.add_node_subclasses(l2_menu_items, self.active_path_ids)
            return
            
        l2_active_path_node_id = self.active_path_ids[1]
        
        # returns None or a queryset
        sub_menu_items = self.get_left_menu_nodes(self.selected_node, l2_active_path_node_id) 
        
        if sub_menu_items is None or sub_menu_items.count()==0:      # nothing found, menu_items are the l2 items            
            self.menu_items = NodeProcessor.add_node_subclasses(l2_menu_items, self.active_path_ids)
            return
            
        # at the L2 level, insert the sub_menu_items
        all_menu_items = []
        for idx, l2_mi in enumerate(l2_menu_items):
            all_menu_items.append(l2_mi)
            if l2_mi.id == sub_menu_items[0].parent.id:        # check above that sub_menu_items.count() is > 0
                all_menu_items += sub_menu_items    
        
        self.menu_items = NodeProcessor.add_node_subclasses(all_menu_items, self.active_path_ids)
    
    def get_menu_by_level(self, level, include_root_node=False):
        """Retrieve the menu for any given depth.  
            root node - level 1
            parent is root - level 2
        etc."""
        if (level is None) or str(level).isdigit() is False: 
            return None

        qs1 = Node.objects.select_related('parent').filter(visible=True)

        if include_root_node:
            qs2 = qs1.filter(Q(menu_level=level) | Q(menu_level=1)).order_by('left_val', 'sibling_order')
        else:
            qs2 = qs1.filter(menu_level=level).order_by('left_val', 'sibling_order')
        
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

    def set_breadcrumb_nodes(self):
        """For a given node, retrieve the breadcrumb nodes.
         Ordered with the root appearing first

         To exclude the selected node, the last node in the breadcrumb trail,
         set breadcrumb_exclude_selected_node to True
        """
        self.breadcrumb_nodes = []
        selected_node = self.selected_node
        if selected_node is None:
            return None

        # include the selected node, neeeded for active_path_ids
        qs = Node.objects.filter(visible=True\
                    , left_val__lte=selected_node.left_val\
                    , right_val__gte=selected_node.right_val).order_by('left_val')

        self.active_path_ids = map(lambda x: x.id, qs)      # pull the active path ids for later use
        
        # exclude selected node from breadcrumb
        if self.breadcrumb_exclude_selected_node:       
            qs2 = qs.exclude(id=selected_node.id)
            self.breadcrumb_nodes = NodeProcessor.add_node_subclasses(qs2) 
        else:
            # regular breadcrumb
            self.breadcrumb_nodes = NodeProcessor.add_node_subclasses(qs) 
        
       
        