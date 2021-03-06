class OrOperator:
    def __init__(self, children):
        self.children = children

    def test(self, prop_dict):
        # If any of them are true, then ORing all of them would be true
        return any(child.test(prop_dict) for child in self.children)

    def __repr__(self):
        return "OR[%s]" % ", ".join(map(str, self.children))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.children == other.children
        else:
            return False

    def __ne__(self, other):
        return not (self == other)

    @property
    def schema(self):
        return reduce(lambda total, next: (total | next.schema), self.children, set())

    def apply_to(self, tree):
        """
        Apply the current query to a traversal tree.
        """
        # OR operator, so we can't split it
        tree.add_query(self)
