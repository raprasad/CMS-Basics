
# Minimal classes to create pages with a hierarchical menu.
-- (more documentation to come on how to actually use this)

Basic building blocks:

# cms_menu_node
## Node 
* base class for a menu item
* Uses a Modified Preorder Tree Traversal as detailed here: http://blogs.sitepoint.com/hierarchical-data-database-2/	
* This is not a tree built for high volume changes--saving a node rebuilds the entire tree

# cms_page
## Page(Node)
* Inherits from Node.  Includes an author, page content, etc

## PageDirectLink(Node)
* Inherits from node and directly links to an outside page. e.g., a link on the menu goes to a specific url.  Created for menu links that go off site.

## PageCustomView(Node)
* Inherits from Node.  This menu item points to a view name.  May not be the best way to do this.
* cms_page/verify_all_page_custom_views.py -> verify_all_page_custom_views()
* This function can be called to make sure that the names specified in the PageCustomView exist in the project's urls.py

# Dependencies
* (Poor-Man's-Tag)[https://github.com/raprasad/Poor-Mans-Tag], contains one Tag model with 5 attributes
* (django-ckeditor)[https://github.com/raprasad/django-ckeditor], for using the ckeditor with a filebrowser for uploaded files.  The dependency may be removed by searching for/removing 'CKEditorWidget'
