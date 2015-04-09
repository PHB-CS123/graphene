class MatchNode:
    def __init__(self, name, node_type):
        self.name = name
        self.type = node_type

    def __repr__(self):
        if self.name is not None:
            return "{Node: %s as '%s'}" % (self.type, self.name)
        else:
            return "{Node: %s}" % self.type
