from django.contrib import admin

from cms_page.models import PageImage, PageDocument

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