
class ParentRelationshipCircular(Exception):
    """Used to raise an exception when saving a Node"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return """The Parent relationship is circular for node [%s]!  Please choose another parent!  (Or no parent for a root node)""" % (self.value)