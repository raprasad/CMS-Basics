from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save     

from django.conf import settings

from cms_common.msg_util import *

from cms_menu_node.models import Node
from cms_menu_node.tree_builder import rebuild_tree_after_node_saved

#from ckeditor.fields import RichTextField
from django.contrib.sites.models import Site



class Page(Node):
    """ 
    A CMS Page object
    
    Basic page content, including where the page falls within the navigation
    """
    author = models.ForeignKey(User)
    title = models.CharField('title', max_length=200, help_text='The title of the page.')

    content = models.TextField() #RichTextField(config_name='default')   
        
    teaser = models.TextField(blank=True, help_text='For an RSS feed or other short format')
    #teaser = RichTextField(blank=True, help_text='For an RSS feed or other short format')

    template = models.FilePathField(path=settings.PAGE_TEMPLATE_DIRECTORY, blank=True, help_text='default is to not use template')#, null=True)
    #assigned_view = models.CharField()

    start_publish_date = models.DateTimeField('start publishing', null=True, blank=True, help_text='optional, if not filled in, active if "visible" is set')
    end_publish_date = models.DateTimeField('finish publishing', null=True, blank=True, help_text='optional, if not filled in, active if "visible" is set')

    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True)

    # Access
    requires_login = models.BooleanField('requires login', help_text='If checked, only logged-in users can view the page.')

    def __unicode__(self):
        return self.title
        
    
    def get_page_url_by_id(self):
        return reverse('view_page_by_id', kwargs={ 'page_id' : self.id })
        
    def get_page_url_by_slug(self):
        return reverse('view_page_by_slug', kwargs={ 'page_slug' : self.slug })
    
    def get_page_by_id_and_slug(self):
        return reverse('view_page_by_id', kwargs={ 'page_id' : self.id, 'page_slug' : self.slug  })
    
    def get_absolute_url(self):
        return self.get_page_url_by_slug()

    
    def save(self, **kwargs):
        """For children, set the subclass_name here!"""      
        self.subclass_name = self.__class__.__name__

        super(Page, self).save(**kwargs)

class PageCustomView(Node):
    """Menu item points to a view name.  May not be the best way to do this.
    First Attempt at it"""
    
    url_name = models.CharField(max_length=255, help_text='Needs to exist in the projects urls.py files')
    url_has_slug_attribute = models.BooleanField(default=True, help_text='optional')
    url_has_id_attribute = models.BooleanField(help_text='optional')

    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True)
    
    
    def get_absolute_url(self):
        """Reverses the 'url_name', using the slug and id as kwargs
        May add ability for custom attributes in next version"""
        custom_view_kwargs = {}
        if self.url_has_slug_attribute:
            custom_view_kwargs.update( {  'page_slug' : self.slug })
        if self.url_has_id_attribute:
            custom_view_kwargs.update( {  'page_id' : self.id })
        
        #print self.url_name, custom_view_kwargs
        return reverse(self.url_name, kwargs=custom_view_kwargs)
        
    def save(self, **kwargs):
        """For children, set the subclass_name here!"""      
        self.subclass_name = self.__class__.__name__

        super(PageCustomView, self).save()
        
                    
class PageDirectLink(Node):
    """Inherits from node and directly links to an outside page

    Basic page content, including where the page falls within the navigation
    """
    direct_url = models.URLField(max_length=255)
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    modified = models.DateTimeField(null=True, blank=True, auto_now=True)

    # Access
    requires_login = models.BooleanField('requires login', help_text='If checked, only logged-in users can view the page.')

    def get_absolute_url(self):
        return self.direct_url

    def save(self, **kwargs):
        """For children, set the subclass_name here!"""      
        self.subclass_name = self.__class__.__name__

        super(PageDirectLink, self).save()

class PageDocument(models.Model):
    """File uploads for a specific page"""
    page = models.ForeignKey(Page)
    nickname = models.CharField(max_length=255)
    doc_file = models.FileField(max_length=255, upload_to='docs')
    entry_time = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return '%s - %s' % (self.page, self.nickname)

    def doc_path(self):
        #return '<h1>blah</h1>'
        return '<input type="text" value="http://%s%s" />' % (Site.objects.get_current().domain,\
                                        self.doc_file.url )
    doc_path.allow_tags = True

    class Meta:
        ordering = ('nickname', 'entry_time')

class PageImage(models.Model):
    """Image uploads for a specific page"""

    page = models.ForeignKey(Page)
    nickname = models.CharField(max_length=255)
    image_file = models.FileField(max_length=255, upload_to='imgs/pages')
    entry_time = models.DateTimeField(auto_now_add=True)

    def web_url(self):
        #return '<h1>blah</h1>'
        return '<img src="%s" width="100" /><br /><input type="text" value="http://%s%s" />' % ( self.image_file.url,\
                                        Site.objects.get_current().domain,\
                                        self.image_file.url )
    web_url.allow_tags = True

    def __unicode__(self):
        return '%s - %s' % (self.page, self.nickname)

    class Meta:
        ordering = ('nickname', 'entry_time')


#post_save.connect(rebuild_tree_after_node_saved, sender=Page)
#post_save.connect(rebuild_tree_after_node_saved, sender=PageCustomView)
#post_save.connect(rebuild_tree_after_node_saved, sender=PageDirectLink)


"""
Does this make sense?  
    - get a list of url names to evaluate against on save
    - can the kwarg argument be overloaded?
    
    ,    url(r'faculty-listing/$', 'view_faculty_listing', name='view_faculty_listing')
    -> makes sense
        
    -> but how would this work for say a faculty detail page -- if you don't want a faculty member to be a subclass of Node
    
    # use faculty-detail "base" to make urls
    # what about the breadcrumb?  why not: home -> faculty listing -> faculty detail: ?page_title?
    ,    url(r'faculty-detail/$', 'view_faculty_detail', name='view_faculty_detail_base')
    ,    url(r'faculty-detail/(?P<slug>\d{1,7})/$', 'view_faculty_detail', name='view_faculty_detail')
    
    
    
class PageCustomView(Node):

    #view_name = models.CharField('title', max_length=255')
    url_name = models.CharField('title', max_length=255')   # url is attached to a view
    
    def get_absolute_url(self):
        
        return reverse(self.url_name, kwargs={'id':self.id, 'slug':self.slug}
        
"""


