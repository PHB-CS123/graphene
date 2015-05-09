class AndOperator:
    def __init__(self, children):
        self.children = children

    def test(self, prop_dict):
        # If all of them are true, then ANDing all of them would be true
        return all(child.test(prop_dict) for child in self.children)

    def __repr__(self):
        return "AND[%s]" % ", ".join(map(str, self.children))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.children == other.children
        else:
            return False

    def __ne__(self, other):
        return not (self == other)
