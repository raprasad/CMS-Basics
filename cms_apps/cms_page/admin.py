from django.contrib import admin

from cms_page.models import Page, PageDirectLink, PageCustomView, PageImage, PageDocument
from cms_page.forms import PageAdminForm, PageDirectLinkAdminForm, PageCustomViewAdminForm
from cms_menu_node.admin import NodeAdminBase
"""
Have base class/subclass for ModelAdmin?  B/c node info is repeated over and over?
"""
   
 

class PageImageInline(admin.TabularInline):
    model = PageImage
    #form = CageDataForm
    readonly_fields= ['entry_time', 'web_url', ]
    fields = ['nickname', 'image_file', 'web_url',]
    extra=0
 
class PageDocumentInline(admin.TabularInline):
    model = PageDocument
    #form = CageDataForm
    readonly_fields= ['entry_time', 'doc_path', ]
    fields = ['nickname', 'doc_file', 'doc_path',]
    extra=0

 
class PageAdmin(NodeAdminBase):
 
    form = PageAdminForm
    
    inlines = (  PageImageInline, \
               # , ESCellColonyProcessingAdminInline \
                )
                
    readonly_fields = ('is_root', 'slug', 'breadcrumb', 'menu_level', 'left_val', 'right_val',  'subclass_name', 'created', 'modified')
    fieldsets = [
             ('Name / Parent', {'fields': ['name' \
                , 'parent'\
                , 'visible'\
                , 'sibling_order'\
                ]})\
            ,('Content', {'fields': [  'author', 'title', 'template' , 'content', 'teaser', ]})            
            ,('Navigation (auto-filled)', {'fields': [ ('menu_level', 'is_root'),'breadcrumb', 'slug', ]})
            ,('Time Stamps', {'fields': [  ('start_publish_date', 'end_publish_date',), ('modified', 'created'), ]})
             ,('for Modified Preorder Tree Traversal', {'fields': [ ('left_val', 'right_val'), ]})
            , ('Render Conveniences', {'fields': [ 'subclass_name',  ]}),                
         ]

    
admin.site.register(Page, PageAdmin)


class PageCustomViewAdmin(admin.ModelAdmin):
    form = PageCustomViewAdminForm
    save_on_top = True
    readonly_fields = ('is_root', 'slug', 'breadcrumb', 'menu_level', 'left_val', 'right_val',  'subclass_name', 'created', 'modified', )
    
    fieldsets = [
             ('Name / Parent', {'fields': ['name' \
                , 'url_name' \
                , ('url_has_slug_attribute', 'url_has_id_attribute', )
                , 'parent'\
                , 'visible'\
                , 'sibling_order'\
                ]})\
            ,('Navigation (auto-filled)', {'fields': [ ('menu_level', 'is_root'),'breadcrumb', 'slug', ]})
            ,('Time Stamps', {'fields': [   ('modified', 'created'), ]})
             ,('for Modified Preorder Tree Traversal', {'fields': [ ('left_val', 'right_val'), ]})
            , ('Render Conveniences', {'fields': [ 'subclass_name',  ]}),                
         ]
admin.site.register(PageCustomView, PageCustomViewAdmin)
    
         
class PageDirectLinkAdmin(admin.ModelAdmin):
    form = PageAdminForm
    readonly_fields = ('is_root', 'slug', 'breadcrumb', 'menu_level', 'left_val', 'right_val',  'subclass_name', 'created', 'modified', 'direct_url')
    
    fieldsets = [
             ('Name / Parent', {'fields': ['name' \
                , 'direct_url' \
                , 'parent'\
                , 'visible'\
                , 'sibling_order'\
                ]})\
            ,('Navigation (auto-filled)', {'fields': [ ('menu_level', 'is_root'),'breadcrumb', 'slug', ]})
            ,('Time Stamps', {'fields': [   ('modified', 'created'), ]})
             ,('for Modified Preorder Tree Traversal', {'fields': [ ('left_val', 'right_val'), ]})
            , ('Render Conveniences', {'fields': [ 'subclass_name',  ]}),                
         ]

    
admin.site.register(PageDirectLink, PageDirectLinkAdmin)
