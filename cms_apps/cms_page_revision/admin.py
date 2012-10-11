from django.contrib import admin
from cms_page.models import Page, EDIT_ONLY_OWN_PAGES_GROUP
from cms_page.admin_base import PageImageInline, PageDocumentInline
from cms_page.forms import PageAdminForm
from cms_page_revision.models import PageRevision


# unregister Page from the version in cms_page/admin.py
admin.site.unregister(Page)


class PageRevisionAdmin(admin.ModelAdmin):
    model = PageRevision
    list_display = ('page', 'name', 'title','revision_date', )
    list_filter = ('page', )
    readonly_fields = ('page', 'name', 'title', 'content', 'teaser', 'slug', 'revision_date', 'restore_version', 'rendered_content')
    fieldsets = [
             ('Name / Parent', {'fields': ['revision_date' \
                , 'restore_version'
                , 'name'\
                , 'title'\
                , 'content'\
                , 'teaser'\
                , 'rendered_content'
                ]})\
            ]
admin.site.register(PageRevision, PageRevisionAdmin)


class PageRevisionInline(admin.TabularInline):
    model = PageRevision
    extra=0
    readonly_fields = ('page', 'name', 'title', 'content'\
                    , 'teaser', 'slug', 'revision_date'\
                    , 'restore_version', 'view_revision'\
                     )
    list_display= ('revision_date', 'name', 'title', 'content', 'teaser',)
    fieldsets = [
             ('Name / Parent', {'fields': ['revision_date' \
                , 'restore_version'
                , 'view_revision'
                , 'name'\
                , 'title'\
                , 'teaser'\
                ]})\
            ]
    


    
class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    save_on_top = True
    inlines = (PageImageInline, \
                PageDocumentInline, \
                PageRevisionInline,\
                )
    
    filter_horizontal = ('tags',)
    readonly_fields = ('is_root', 'slug', 'breadcrumb', 'menu_level', 'left_val', 'right_val', 'created', 'modified', 'subclass_name', 'preview_page',)# 'get_absolute_url')
    list_editable = ('sibling_order', )
    list_filter = ('visible', 'menu_level',)
    list_display = ('name', 'breadcrumb', 'sibling_order','menu_level', 'visible', 'is_root',  'left_val', 'right_val', )
    search_fields = ('name',)
    fieldsets = [
             ('Name / Parent', {'fields': ['name' \
                , 'parent'\
                , ('visible', 'preview_page',)\
                , 'sibling_order'\
                ]})\
            ,('Content', {'fields': [  'author', 'title', 'template' , 'content', 'teaser', ]})            
            , ('Tags', {'fields': ['tags']})     
            
            ,('Navigation (auto-filled)', {'fields': [ ('menu_level', 'is_root'),'breadcrumb', 'slug', ]})
            ,('Time Stamps', {'fields': [  ('start_publish_date', 'end_publish_date',), ('modified', 'created'), ]})
             ,('for Modified Preorder Tree Traversal', {'fields': [ ('left_val', 'right_val'), ]})
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


    class Media:
        pass
    #    js = ('ckeditor/ckeditor/ckeditor.js',)
    #    js = ('js/tiny_mce/tiny_mce.js', \
    #        'js/tiny_mce/textareas.js',)
                
admin.site.register(Page, PageAdmin)

