class NodeProperty:
    def __init__(self, node, properties, node_type, type_name):
        self.node = node
        self.index = node.index
        self.properties = properties
        self.type = node_type
        self.type_name = type_name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.node == other.node
        else:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        return "%s%s" % (self.type_name, self.properties)
