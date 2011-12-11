from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response

from cms_menu_node.models import Node
from cms_page.models import Page
from cms_menu_builder.menu_builder import build_menu


def view_cms_page_by_id(request, page_id):
    
    lu = {}
    try:
        page = Page.objects.get(id=page_id)
    except DoesNotExist:
        return render_to_response(page.template, lu, context_instance=RequestContext(request))
    
    nodes = build_menu(Node.objects.select_related('parent').filter(visible=True).order_by('left_val', 'right_val'))
    
    lu.update({'page': page \
            , 'nodes' : nodes
            #, 'nodes' : Node.objects.select_related('parent').filter(visible=True).order_by('left_val', 'right_val')
    })

    return render_to_response(page.template, lu, context_instance=RequestContext(request))
    
    
def view_cms_page_by_slug(request, page_id, page_slug):
    try:
        page = Page.objects.get(slug=page_slug)
    except DoesNotExist:
        return render_to_response(page.template, lu, context_instance=RequestContext(request))

    return view_cms_page_by_id(request, page.id)
    

def view_cms_page_by_id_and_slug(request, page_id, page_slug):
    return view_cms_page_by_id(request, page_id)