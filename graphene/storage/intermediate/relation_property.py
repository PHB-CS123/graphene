class RelationProperty:
    def __init__(self, rel, properties, rel_type, type_name):
        self.rel = rel
        self.index = rel.index
        self.properties = properties
        self.type = rel_type
        self.type_name = type_name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.rel == other.rel
        else:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return "%s%s" % (self.type_name, self.properties)
