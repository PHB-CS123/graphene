class MatchRelation:
    def __init__(self, name, rel_type):
        self.name = name
        self.type = rel_type

    def __repr__(self):
        if self.name is not None:
            return "{Relation: %s as '%s'}" % (self.type, self.name)
        else:
            return "{Relation: %s}" % self.type
