from django.db import models
from cms_page.models import Page
from django.core.urlresolvers import reverse

class PageRevision(models.Model):
    """Save a page's title, slug, and content for possible restoration.
Each time a Page is modified, a revision is created."""
    page = models.ForeignKey(Page)
    
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    
    title = models.CharField(max_length=255)
    content = models.TextField()    
    teaser = models.TextField(blank=True)
    
    revision_date = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_attributes_to_check():
        return ['name', 'title', 'content', 'teaser', ]
    
    
    @staticmethod
    def get_attributes_to_restore():
        return ['name', 'title', 'content', 'teaser', 'slug']

    def rendered_content(self):
        return  self.content
    rendered_content.allow_tags = True
    
    def view_revision(self):
        #return reverse('view_restore_revision', kwargs={'revision_id':self.id})
        change_url = reverse('admin:cms_page_revision_pagerevision_change', args=(self.id,))
        return '<a href="%s" target="_blank">view revision</a>' % change_url
    view_revision.allow_tags = True

    def restore_version(self):
        #return reverse('view_restore_revision', kwargs={'revision_id':self.id})
        if not self.id:
            return ''
            
        restore_link = reverse('view_restore_revision', kwargs={'revision_id':self.id})
        return '<a href="%s">restore version</a>' % restore_link
    restore_version.allow_tags = True
        
    def __unicode__(self):
        return self.title
    
    class Meta:
        ordering = ('page', '-revision_date',)
    
from cms_page_revision.revision_manager import connect_revision_signal
connect_revision_signal()


