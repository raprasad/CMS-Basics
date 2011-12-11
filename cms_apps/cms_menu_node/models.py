from django.db import models
from django.template.defaultfilters import slugify

from cms_common.msg_util import *
from cms_menu_node.exceptions import ParentRelationshipCircular


BREADCRUMB_SEPARATOR = '->'
STR_NOT_VISIBLE = '(not visible)'
class Node(models.Model):
    """Base class for a menu item
    Initial use is to use this for a CMS and create subclasses as needed.
    Uses a Modified Preorder Tree Traversal as detailed here:
     http://blogs.sitepoint.com/hierarchical-data-database-2/
    """
    name = models.CharField('menu name', max_length=255, unique=True)
    slug = models.SlugField(max_length=255, blank=True, help_text='(auto-filled on save)')
    
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    visible = models.BooleanField(default=True)    # if visible is false, node is not included in 
     
    sibling_order = models.IntegerField(default=1, help_text='relative ordering among siblings')     # used for sibling sorting
    is_root = models.BooleanField(default=False, help_text='(auto-filled on save)')
    menu_level = models.IntegerField(default=-1, help_text='(auto-filled on save)')
    left_val = models.IntegerField(default=-1, help_text='(auto-filled on save)')
    right_val = models.IntegerField(default=-1, help_text='(auto-filled on save)')
    
    # auto-filled by subclasses
    subclass_name = models.CharField(max_length=255, blank=True, default='')
    
    
    def show(self):
        attrs = 'id name slug parent visible sibling_order is_root menu_level left_val right_val subclass_name'.split()
        dashes()
        for attr in attrs:
            msg('%s: [%s]' % (attr, self.__dict__.get(attr, None)))
    
    def __unicode__(self):   
        return self.name        
    
        
    def get_absolute_url(self):
        # for subclass overrides
        return 'Node.get_absolute_url - override this function'
        
    
    def parent_string_for_admin(self):  
        """Based on parental relationships.
        Inefficient in terms of querying but exact if left/right vals are out of sync.
        The MPTT replacement is in function "breadcrumb"
        """
        if self.is_root:
            return self.name 
        elif self.parent is None:
            return self.name    # shouldn't happen
        else:
            if self.visible:
                return '%s %s %s' % (self.parent.parent_string_for_admin(), BREADCRUMB_SEPARATOR,  self.name)
            else:
                return '%s %s %s (%s)' % (self.parent.parent_string_for_admin(), BREADCRUMB_SEPARATOR,  self.name, STR_NOT_VISIBLE)
                
            #return '%s %s' % (' -- | -- ' * (self.menu_level-1), self.name)
        
        
    def set_menu_level(self):
        mlevel = Node.objects.filter(left_val__lt=self.left_val\
                            , right_val__gt=self.right_val).count()
        if mlevel == 0 and self.parent is not None:
            self.menu_level = -1
        else:
            self.menu_level = mlevel + 1


    def get_nodes_on_path(self):
        pass

    def breadcrumb(self, exclude_leaf_node=False):
        """Based on the rt/left MPTT values"""
        if self.is_root:
            return self.name
            
        if exclude_leaf_node:       # lt / gt - exclude leaf
            qs = Node.objects.filter(left_val__lt=self.left_val, right_val__gt=self.right_val).order_by('left_val')
        else:                       # lte / gte - include leaf
            qs = Node.objects.filter(left_val__lte=self.left_val, right_val__gte=self.right_val).order_by('left_val')
            
        breadcrumb_names = map(lambda x: x.name, qs)
        #print qs
        #print breadcrumb_names
        sep = ' %s ' % BREADCRUMB_SEPARATOR
        return sep.join(breadcrumb_names)
        
    """
    def breadcrumb(self):
        if not self.visible:
            return '%s %s' % (self.name, STR_NOT_VISIBLE)

        if self.parent is None:
            return self.name
        
        return '%s %s %s' % (self.parent.breadcrumb(), BREADCRUMB_SEPARATOR, self.name)
    """    
    def breadcrumb_without_leaf(self):
        return self.breadcrumb(exclude_leaf_node=True)
        
    
    def is_left_node(self):
        """A leaf node has no desendants"""
        if self.get_num_descendants() == 0:
            return True
        return False
    
    def has_descendants(self):
        if self.get_num_descendants() > 0:
            return True
        return False
        
    def get_num_descendants(self):
        """Return the descendant count for a particular node"""
        if self.left_val > -1 and self.right_val > -1:  # are lft and right set?
            if self.right_val > self.left_val:  # should always be true
                return (self.right_val - self.left_val - 1) / 2
                
        # something is wrong with lft/rt vals -- or they are not set
        return -1
    
    def delete(self):
        """Before deleting the node, assign a new parent to its children 
        and clear the parent FK connections"""

        disconnect_node_signals()

        children = self.node_set.all()
        if children.count() > 0:        # does the node have children
            if self.is_root:            # is this the root mode
                new_parent = children[0]    # new parent is 1st child; awkward but preserves family:)
                new_parent.parent = None    # makes parent the new root
                new_parent.save()
            else:
                new_parent = self.parent    # new parent is grandparent

            for c in children:
                if c.id == new_parent.id:
                    pass    # if self is a root node, pass, new root will be this child
                else:
                    c.parent = new_parent                    
                    c.save()
                        
        self.node_set.clear()   # clear the FK connections

        connect_node_signals()                                
        super(Node, self).delete()
        #rebuild_tree_after_node_saved()
     
     
    def save(self, **kwargs):
        #msgt('NODE save: %s' % self.name)
        """Note pre_save and post_save signals are used.

        > pre_save: make sure there are no duplicate roots
        > post_save: reassign left/root values to the tree

        - kwargs used so unit tests run correctly

        """
        if Node.is_parent_relationship_circular(self, self.parent):
            raise ParentRelationshipCircular(self)
                
        # this node being assigned as a root
        if self.parent is None:
            self.is_root = True
        else:
            self.is_root = False   

        self.slug = slugify(self.name)
        
        super(Node, self).save(kwargs)
    
    class Meta:
        ordering = ('left_val', )


    @staticmethod
    def get_admin_parent_choices():
        # Used in the admin for display of the "parent" attribute--to show its menu level
        #
        #   usual: __unicode__(self)
        #   replacement: __parent_string_for_admin__(self)
        #
        choices = map(lambda x: (x.id, x.parent_string_for_admin()), Node.objects.filter(visible=True))
        if len(choices) == 0:
            return [('', '----------')]
        else:
            return choices

    @staticmethod
    def is_parent_relationship_circular(instance, new_parent):
        """
            Make sure parent relationship isn't circular
            e.g. you don't want parent relations such as below:

            "<-" = "parent of"

            ex 1/   red <- apple
                    apple <- red
            ex 2/   food <- fruit <- yellow <- banana
                    banana <- food
            etc.            
        """
        if new_parent and instance:
            if instance.id == new_parent.id:
                return True
                
        # This will be a new root
        if instance and new_parent is None:           
            return False

        # case: p1 -> p1    
        if instance == new_parent or instance == instance.parent:
            return True

        parent = new_parent
        plist = [instance]
        while parent:
            if parent in plist:
                return True
            plist.append(parent)
            parent = parent.parent     
        
        return False

# ------------------------------------------
# SIGNALS for saving a node
# ------------------------------------------

from cms_menu_node.tree_builder import connect_node_signals, disconnect_node_signals, rebuild_tree_after_node_saved
connect_node_signals()  # connect signals to rebuild tree and ensure one, and only one, root node
#check_for_single_root, rebuild_tree_after_node_saved

# ------------------------------------------
# pre save: make sure there is one, and only one, root
# ------------------------------------------
#pre_save.connect(check_for_single_root, sender=Node)

# ------------------------------------------
# post save: rebuild the tree
# ------------------------------------------
#post_save.connect(rebuild_tree_after_node_saved, sender=Node)

