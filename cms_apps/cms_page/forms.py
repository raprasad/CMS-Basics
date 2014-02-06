from django import forms
from cms_page.models import Page, PageDirectLink, PageCustomView, PagePlaceHolder
from cms_menu_node.models import Node

from ckeditor.fields import CKEditorWidget

from verify_page_custom_views import get_list_of_all_urls


class PageAdminForm(forms.ModelForm):
    """Admin Form for a Node
    - Updates the parent choices to include indentations (displayed as a select box)
    - Checks to make sure the parent relationship is not circular
    - Some formatting of the parent Select box, and teaser TextBox
    """
    def __init__(self, *args, **kwargs):
        super(PageAdminForm, self).__init__(*args, **kwargs)
        self.fields['parent'].choices = Node.get_admin_parent_choices()
        
        # If the root already exist, don't let people accidentally change it
        # This is for "regular" users once this thing is in production.
        #if Node.objects.filter(visible=True).count() >= 2:
        #    if self.instance and self.instance.is_root:
        #        pass
        #    else:
        #        self.fields['parent'].required = True    
        
    class Meta:
        model = Page
        widgets = {  'parent': forms.Select(attrs={'size': 10, 'width':100}) \
                    , 'content' : CKEditorWidget(config_name='default', attrs={}) \
                    ,'teaser': forms.Textarea(attrs={'rows':3, 'cols':40}) \
                    }
    
    def clean_parent(self):    
        new_parent = self.cleaned_data['parent']

        if Node.is_parent_relationship_circular(self.instance, new_parent=new_parent):
            raise forms.ValidationError("The Parent relationship is circular!  Please choose another parent!  (Or no parent for a root node)")
        
        if Node.does_root_node_already_exist(self.instance) and not new_parent:
            raise forms.ValidationError("Please choose a parent.  (A home/root node already exists.)")
                
        return new_parent        

class PageCustomViewAdminForm(forms.ModelForm):
    """Admin Form for a Node
    - Updates the parent choices to include indentations (displayed as a select box)
    - Checks to make sure the parent relationship is not circular
    - Some formatting of the parent Select box
    """
    def __init__(self, *args, **kwargs):
        super(PageCustomViewAdminForm, self).__init__(*args, **kwargs)
        self.fields['parent'].choices = Node.get_admin_parent_choices()


    class Meta:
        model = PageCustomView
        widgets = {  'parent': forms.Select(attrs={'size': 10, 'width':100}) }


    
    def clean_url_name(self):
        url_name = self.cleaned_data['url_name']
        if not url_name in get_list_of_all_urls():
            raise forms.ValidationError("That url_name does not exist this project's urls.py files")
        
        return url_name
            
        
    def clean_parent(self):    
        new_parent = self.cleaned_data['parent']

        if Node.is_parent_relationship_circular(self.instance, new_parent=new_parent):
            raise forms.ValidationError("The Parent relationship is circular!  Please choose another parent!  (Or no parent for a root node)")

        if Node.does_root_node_already_exist(self.instance) and not new_parent:
            raise forms.ValidationError("Please choose a parent.  (A home/root node already exists.)")

        return new_parent             

class PageDirectLinkAdminForm(forms.ModelForm):
    """Admin Form for a Node
    - Updates the parent choices to include indentations (displayed as a select box)
    - Checks to make sure the parent relationship is not circular
    - Some formatting of the parent Select box
    """
    def __init__(self, *args, **kwargs):
        super(PageDirectLinkAdminForm, self).__init__(*args, **kwargs)
        self.fields['parent'].choices = Node.get_admin_parent_choices()


    class Meta:
        model = PageDirectLink
        widgets = {  'parent': forms.Select(attrs={'size': 10, 'width':100}) \
                    }

    def clean_parent(self):    
        new_parent = self.cleaned_data['parent']

        if Node.is_parent_relationship_circular(self.instance, new_parent=new_parent):
            raise forms.ValidationError("The Parent relationship is circular!  Please choose another parent!  (Or no parent for a root node)")

        if Node.does_root_node_already_exist(self.instance) and not new_parent:
            raise forms.ValidationError("Please choose a parent.  (A home/root node already exists.)")
        return new_parent        




class PagePlaceHolderAdminForm(forms.ModelForm):
    """Admin Form for a Node
    - Updates the parent choices to include indentations (displayed as a select box)
    - Checks to make sure the parent relationship is not circular
    - Some formatting of the parent Select box
    """
    def __init__(self, *args, **kwargs):
        super(PagePlaceHolderAdminForm, self).__init__(*args, **kwargs)
        self.fields['parent'].choices = Node.get_admin_parent_choices()


    class Meta:
        model = PagePlaceHolder
        widgets = {  'parent': forms.Select(attrs={'size': 10, 'width':100}) \
                    }

    def clean_parent(self):    
        new_parent = self.cleaned_data['parent']

        if Node.is_parent_relationship_circular(self.instance, new_parent=new_parent):
            raise forms.ValidationError("The Parent relationship is circular!  Please choose another parent!  (Or no parent for a root node)")

        if Node.does_root_node_already_exist(self.instance) and not new_parent:
            raise forms.ValidationError("Please choose a parent.  (A home/root node already exists.)")
        return new_parent        


   