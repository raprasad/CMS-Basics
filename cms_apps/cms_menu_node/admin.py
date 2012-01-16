from django.contrib import admin

from cms_menu_node.models import Node
from cms_menu_node.admin_base import NodeAdminBase
from cms_menu_node.forms import NodeAdminForm


class NodeAdmin(NodeAdminBase):

    form = NodeAdminForm
    filter_horizontal = ('tags',)
    fieldsets = [
             ('Name / Parent', {'fields': ['name' \
                , 'parent'\
                , 'visible'\
                , 'sibling_order'\
                , 'tags'
                ]}),\
            ('Navigation', {'fields': [ 'menu_level', 'is_root','breadcrumb', 'slug', ]}),                
             ('for Modified Preorder Tree Traversal', {'fields': [ ('left_val', 'right_val'), ]}),                
             ('Render Conveniences', {'fields': [ 'subclass_name',  ]}),                
         ]
    
    
admin.site.register(Node, NodeAdmin)
