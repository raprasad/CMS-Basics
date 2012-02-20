from django.contrib import admin

class NodeAdminBase(admin.ModelAdmin):
    save_on_top = True
    readonly_fields = ['is_root', 'slug', 'breadcrumb', 'menu_level', 'left_val', 'right_val',  'subclass_name', 'is_first_sibling', 'is_last_sibling', 'parent_node_id']
    list_editable = ('sibling_order',)
    list_filter = ('visible', 'menu_level',)
    list_display = ('name', 'breadcrumb', 'sibling_order','menu_level', 'visible', 'is_root',  'left_val', 'right_val', )
    search_fields = ('name',)

