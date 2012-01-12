
class ParentRelationshipCircular(Exception):
    """Used to raise an exception when saving a Node"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return """The Parent relationship is circular for node [%s]!  Please choose another parent!  (Or no parent for a root node)""" % (self.value)
        

class RootNodeAlreadyExists(Exception):
    """Used to raise an exception when saving a Node as Root, when root exists"""
    def __init__(self, value):
        self.value=value
        #self.value
        #self.value = value
        
    def __str__(self):
        return """Please choose a parent for node "%s"!  A root node already exists.""" % self.value