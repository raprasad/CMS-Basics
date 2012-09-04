from django.contrib import admin

from cms_page.models import Page, PageDirectLink, PageCustomView, PageImage, PageDocument, EDIT_ONLY_OWN_PAGES_GROUP

from cms_page.forms import PageAdminForm, PageDirectLinkAdminForm, PageCustomViewAdminForm

from cms_menu_node.admin_base import NodeAdminBase

from cms_page.admin_base import PageImageInline, PageDocumentInline


"""
Have base class/subclass for ModelAdmin?  B/c node info is repeated over and over?
"""

 
class PageAdmin(NodeAdminBase):
 
    form = PageAdminForm
    
    inlines = (  PageImageInline, \
               # , ESCellColonyProcessingAdminInline \
                )
                
    readonly_fields = ('is_root', 'slug', 'breadcrumb', 'menu_level', 'left_val', 'right_val',  'subclass_name', 'created', 'modified', 'is_first_sibling', 'is_last_sibling', 'parent_node_id')
    fieldsets = [
             ('Name / Parent', {'fields': ['name' \
                , 'parent'\
                , 'visible'\
                , 'sibling_order'\
                ]})\
            ,('Content', {'fields': [  'author', 'title', 'template' , 'content', 'teaser', ]})       
            , ('Tags', {'fields': ['tags']})     
            ,('Navigation (auto-filled)', {'fields': [ ('menu_level', 'is_root'),'breadcrumb', 'slug', ]})
            ,('Time Stamps', {'fields': [  ('start_publish_date', 'end_publish_date',), ('modified', 'created'), ]})
             ,('for Modified Preorder Tree Traversal', {'fields': [ ('left_val', 'right_val'), ]})
             ,('mptt additional convenience', {'fields': [ ('is_first_sibling', 'is_last_sibling', 'parent_node_id', ),  ]})  
             
            , ('Render Conveniences', {'fields': [ 'subclass_name',  ]}),                
         ]

    def queryset(self, request):

        qs = super(PageAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        try:
            for g in request.user.groups.all(): 
                if g.name == EDIT_ONLY_OWN_PAGES_GROUP:
                    return qs.filter(author=request.user)
        except:
            pass
        return qs
        #return Page.objects.all()
    
admin.site.register(Page, PageAdmin)


class PageCustomViewAdmin(NodeAdminBase):#admin.ModelAdmin):
    form = PageCustomViewAdminForm
    save_on_top = True
    readonly_fields = ('is_root', 'slug', 'breadcrumb', 'menu_level', 'left_val', 'right_val',  'subclass_name', 'created', 'modified',  'is_first_sibling', 'is_last_sibling', 'parent_node_id')
    filter_horizontal = ('tags',)
    
    fieldsets = [
             ('Name / Parent', {'fields': ['name' \
                , 'url_name' \
                , ('url_has_slug_attribute', 'url_has_id_attribute', )
                , 'parent'\
                , 'visible'\
                , 'sibling_order'\
                ]})\
                , ('Tags', {'classes': ('collapse',), \
                    'fields': ['tags']})     \
                
            ,('Navigation (auto-filled)', {'fields': [ ('menu_level', 'is_root'),'breadcrumb', 'slug', ]})
            ,('Time Stamps', {'fields': [   ('modified', 'created'), ]})
             ,('for Modified Preorder Tree Traversal', {'fields': [ ('left_val', 'right_val'), ]})
            ,  ('mptt additional convenience', {'fields': [ ('is_first_sibling', 'is_last_sibling', 'parent_node_id', ),  ]}) 
             
            , ('Render Conveniences', {'fields': [ 'subclass_name',  ]}),                
         ]
admin.site.register(PageCustomView, PageCustomViewAdmin)
    
         
class PageDirectLinkAdmin(admin.ModelAdmin):
    form = PageDirectLinkAdminForm
    readonly_fields = ('is_root', 'slug', 'breadcrumb', 'menu_level', 'left_val', 'right_val',  'subclass_name', 'created', 'modified',  'is_first_sibling', 'is_last_sibling', 'parent_node_id')
    filter_horizontal = ('tags',)
   
    fieldsets = [
             ('Name / Parent', {'fields': ['name' \
                , 'direct_url' \
                , 'parent'\
                , 'visible'\
                , 'sibling_order'\
                ]})\
            , ('Tags', {'classes': ('collapse',), \
                'fields': ['tags']})     \
            ,('Navigation (auto-filled)', {'fields': [ ('menu_level', 'is_root'),'breadcrumb', 'slug', ]})
            ,('Time Stamps', {'fields': [   ('modified', 'created'), ]})
             ,('for Modified Preorder Tree Traversal', {'fields': [ ('left_val', 'right_val'), ]})
             , ('mptt additional convenience', {'fields': [ ('is_first_sibling', 'is_last_sibling', 'parent_node_id', ),  ]})
             
            , ('Render Conveniences', {'fields': [ 'subclass_name',  ]}),                
         ]

admin.site.register(PageDirectLink, PageDirectLinkAdmin)
