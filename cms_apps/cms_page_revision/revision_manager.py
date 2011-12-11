from cms_common.msg_util import *
from cms_page.models import Page
from cms_page_revision.models import PageRevision
from django.db.models.signals import pre_save


def make_revision(page_obj):
    if page_obj is None:
        return False
        
    revision = PageRevision(page=page_obj\
                ,name=page_obj.name\
                ,slug=page_obj.slug\
                ,title=page_obj.title\
                ,content=page_obj.content\
                ,teaser=page_obj.teaser\
            )
    revision.save()        
    #msg('revision saved!')
    return True

def check_for_new_revision(sender=None, **kwargs):
    """Check the page being saved, if it's a revision--create a PageRevision before saving"""
    # sender is a Page object
    #msgt('check_for_new_revision')
    
    page_to_save = kwargs.get('instance', None)
    if page_to_save is None:
        return
        
    if page_to_save.id is None:
        #msg('first time page is being saved, no revision needed')
        return
    
    # retrieve original page from db
    try:
        page_last_saved = Page.objects.get(pk=page_to_save.id)
    except Page.DoesNotExist:
        #msg('original page not found')
        return
        
    change_made = False
    for attr in PageRevision.get_attributes_to_check():
        if not page_to_save.__dict__.get(attr, None) == page_last_saved.__dict__.get(attr, None):
            #print page_to_save.__dict__.get(attr, None)
            #print page_last_saved.__dict__.get(attr, None)
            change_made= True
    
    if not change_made:
        #msg('no changes')
        return
    
    make_revision(page_last_saved)
    
    
def handle_revision_restore(page_revision_obj):
    #msgt('handle_revision_restore')
    if page_revision_obj is None:
        return (False, "Revision not found")
    
    page_to_revise = page_revision_obj.page
    
    #------------------------------
    #disconnect_revision_signal()
    #------------------------------
    for attr in PageRevision.get_attributes_to_restore():
        revision_val = page_revision_obj.__dict__.get(attr, None)
        if revision_val is not None:
            page_to_revise.__dict__.update({attr : revision_val})
    page_to_revise.save()
    #------------------------------
    #connect_revision_signal()
    #------------------------------

    return (True, page_to_revise.id )
    
def connect_revision_signal():
    pre_save.connect(check_for_new_revision, sender=Page)    

def disconnect_revision_signal():
    pre_save.disconnect(check_for_new_revision, sender=Page)    











