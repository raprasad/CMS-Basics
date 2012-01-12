"""
This may be called at any time, and is included in the when the settings file is loading.

It checks whether the urls specified in PageCustomView objects exist somewhere in the projects urls.py files
"""
from django.conf import settings
from cms_page.models import PageCustomView


URL_NAMES = []
def load_url_pattern_names(patterns):
    """Retrieve a list of urlpattern names"""
    global URL_NAMES
    for pat in patterns:
        if pat.__class__.__name__ == 'RegexURLResolver':            # load patterns from this resolver
            load_url_pattern_names(pat.url_patterns)
        elif pat.__class__.__name__ == 'RegexURLPattern':           # load name from this pattern
            if pat.name is not None and pat.name not in URL_NAMES:
                URL_NAMES.append(pat.name)
    return URL_NAMES


URL_NAME_ENDINGS_TO_EXCLUDE = ['changelist' , 'add', 'history', 'delete', 'change']
def does_url_name_have_admin_like_ending(url_name):
    global URL_NAME_ENDINGS_TO_EXCLUDE
    if url_name is None:
        return False
    
    url_name_parts= url_name.split('_')
    if url_name_parts[-1] in URL_NAME_ENDINGS_TO_EXCLUDE:
        return True
    
    return False
    
    
    
def get_list_of_all_urls(remove_admin_urls=True, as_choices=False):
    """Return a list of urls, either as an array or a list of choices for a dropdown box"""
    global URL_NAMES
    
    URL_NAMES = []  # reset global variable
    root_urlconf = __import__(settings.ROOT_URLCONF) 
    url_fname = str(settings.ROOT_URLCONF).split('.')[-1]   # e.g. 'urls_laptop' from 'btvc.urls_laptop'
    url_pattern_name_to_eval = eval('root_urlconf.%s.urlpatterns' % url_fname)
    url_names = load_url_pattern_names(url_pattern_name_to_eval)
    
    #url_names = load_url_pattern_names(root_urlconf.urls.urlpatterns)
    if remove_admin_urls:
        url_names = filter(lambda x: not does_url_name_have_admin_like_ending(x), url_names)
        
    print url_names
    
    if as_choices:
        return map(lambda x: (x, x), url_names)
    else:
        return url_names


def verify_all_page_custom_views():
    return True

    all_urls = get_list_of_all_urls()
    not_found = []
    for cv in PageCustomView.objects.all():
        if cv.url_name not in all_urls:
            not_found.append(cv.url_name)
    if len(not_found) > 0:
        print 'The following urls were not found: %s' % ('\n-'.join(not_found))
        return False
    return True
    
    
    


