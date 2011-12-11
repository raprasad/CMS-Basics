
Minimal classes to create a pages with a hierarchical menu.

Basic building blocks:

# cms_menu_node
## Node 
* base class for a menu item
* Uses a Modified Preorder Tree Traversal as detailed here: http://blogs.sitepoint.com/hierarchical-data-database-2/	

# cms_page
## Page(Node)
* Inherits from Node.  Includes an author, page content, etc

## PageDirectLink(Node)
* Inherits from node and directly links to an outside page. e.g., a link on the menu goes to a specific url.  Created for menu links that go off site.

## PageCustomView(Node)
* Inherits from Node.  This menu item points to a view name.  May not be the best way to do this.
* cms_page/verify_all_page_custom_views.py -> verify_all_page_custom_views()
* This function can be called to make sure that the names specified in the PageCustomView exist in the project's urls.py

