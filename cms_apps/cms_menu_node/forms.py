from django import forms
from cms_menu_node.models import *



class NodeAdminForm(forms.ModelForm):
    """Admin Form for a Node
    - Updates the "parent" choices to include indentations (displayed as a select box)
    - Some formatting of the "parent" Select box
    - Checks to make sure the "parent"" relationship is not circular
    """
    def __init__(self, *args, **kwargs):
        super(NodeAdminForm, self).__init__(*args, **kwargs)
        self.fields['parent'].choices = Node.get_admin_parent_choices()

    class Meta:
        model = Node
        widgets = {  'parent': forms.Select(attrs={'size': 10, 'width':100}\
                    ) }
    
    def clean_parent(self):    
        new_parent = self.cleaned_data['parent']
        
        if new_parent and self.instance:
            if self.instance.id == new_parent.id:
                raise forms.ValidationError("The Parent relationship is circular!  Please choose another parent!")
            

        if Node.is_parent_relationship_circular(self.instance, new_parent=new_parent):
            raise forms.ValidationError("The Parent relationship is circular!  Please choose another parent!  (Or no parent for a root node)")
        
        if Node.does_root_node_already_exist(self.instance) and not new_parent:
            raise forms.ValidationError("Please choose a parent.  (A home/root node already exists.)")
            
        
        return new_parent
        
        