"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}


"""
find: "name": "(\w{1,30})",
replace: "name": "\1",\n\t\t\t"title": "\1",\n\t\t\t"content": "\1",\n\t\t\t"author": "1",

attrs = 'id name slug parent visible sibling_order is_root menu_level left_val right_val subclass_name'.split()
qs = Node.objects.all()
for n in qs:
    p = Page

title
author
content
teaser

"""

