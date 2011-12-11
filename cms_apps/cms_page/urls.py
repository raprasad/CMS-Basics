from django.conf.urls.defaults import *


urlpatterns = patterns(
    'cms_page.views'
    
,    url(r'p/(?P<page_id>\d{1,7})/$', 'view_cms_page_by_id', name='view_page_by_id')
,    url(r'p/(?P<page_slug>(-|\w|_){1,150})/$', 'view_cms_page_by_slug', name='view_page_by_slug')
,    url(r'p/(?P<page_id>\d{1,7})/(?P<page_slug>(-|\w|_){1,150})$', 'view_cms_page_by_id_and_slug', name='view_page_by_id_and_slug')
,
    
)