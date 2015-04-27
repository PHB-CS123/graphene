class Query:
    def __init__(self, name, oper, value):
        self.name = name
        self.oper = oper
        self.value = value

    def test(self, prop_dict):
        try:
            value, tt = prop_dict[self.name]
        except KeyError:
            raise Exception("%s is not a valid property name." % self.name)
        if self.oper == '=':
            return value == self.value
        if self.oper == '!=':
            return value != self.value
        if self.oper == '>=':
            return value >= self.value
        if self.oper == '>':
            return value > self.value
        if self.oper == '<=':
            return value <= self.value
        if self.oper == '<':
            return value < self.value
        return False
