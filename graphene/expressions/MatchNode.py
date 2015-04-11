class MatchNode:
    """
    Wrapper for a node in a match statement.
    """
    def __init__(self, name, node_type):
        """
        :param str name: Name of the node
        :param str node_type: Relation type
        """
        self.name = name
        self.type = node_type

    def __repr__(self):
        if self.name is not None:
            return "{Node: %s as '%s'}" % (self.type, self.name)
        else:
            return "{Node: %s}" % self.type
