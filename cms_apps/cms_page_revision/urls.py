from django.conf.urls.defaults import *


urlpatterns = patterns(
    'cms_page_revision.views'
    
,    url(r'p/(?P<revision_id>\d{1,8})/$', 'view_restore_revision', name='view_restore_revision')
,
    
)