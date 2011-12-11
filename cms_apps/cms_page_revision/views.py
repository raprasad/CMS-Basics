from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from cms_page.models import Page
from cms_page_revision.models import PageRevision
from cms_page_revision.revision_manager import handle_revision_restore

from django.core.urlresolvers import reverse


def view_restore_revision(request, revision_id):
    #return HttpResponse('view_restore_revision')
    try:
        page_revision = PageRevision.objects.get(pk=revision_id)
    except PageRevision.DoesNotExist:
        return HttpResponse('Sorry!  An error occurred.<p>Please click the back button on hour browser.')

    (success, page_id_or_err) = handle_revision_restore(page_revision)
    
    change_url = reverse('admin:cms_page_page_change', args=(page_id_or_err,))
    return HttpResponseRedirect(change_url)