class MatchRelation:
    """
    Wrapper for a relation in a match statement.
    """
    def __init__(self, name, rel_type):
        """
        :param str name: Name of the relation
        :param str rel_type: Relation type
        """
        self.name = name
        self.type = rel_type

    def __repr__(self):
        if self.name is not None:
            return "{Relation: %s as '%s'}" % (self.type, self.name)
        else:
            return "{Relation: %s}" % self.type
