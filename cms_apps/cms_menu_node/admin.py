from django.contrib import admin

from cms_menu_node.models import Node
from cms_menu_node.forms import NodeAdminForm


class NodeAdminBase(admin.ModelAdmin):
    save_on_top = True
    readonly_fields = ['is_root', 'slug', 'breadcrumb', 'menu_level', 'left_val', 'right_val',  'subclass_name',]
    list_editable = ('sibling_order',)
    list_filter = ('visible', 'menu_level',)
    list_display = ('name', 'breadcrumb', 'sibling_order','menu_level', 'visible', 'is_root',  'left_val', 'right_val', )
    search_fields = ('name',)


class NodeAdmin(NodeAdminBase):

    form = NodeAdminForm

    
    fieldsets = [
             ('Name / Parent', {'fields': ['name' \
                , 'parent'\
                , 'visible'\
                , 'sibling_order'\
                ]}),\
            ('Navigation', {'fields': [ 'menu_level', 'is_root','breadcrumb', 'slug', ]}),                
             ('for Modified Preorder Tree Traversal', {'fields': [ ('left_val', 'right_val'), ]}),                
             ('Render Conveniences', {'fields': [ 'subclass_name',  ]}),                
         ]
    
    
admin.site.register(Node, NodeAdmin)
