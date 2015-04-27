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

    @staticmethod
    def parse_chain(storage_manager, chain, type_schema):
        qc = []
        for q in chain:
            if type(q) == tuple:
                # actual query
                name, oper, value = q
                tt = filter(lambda t: t[1] == name, type_schema)
                if len(tt) == 0:
                    # no such named property
                    raise Exception("%s is not a valid property name." % name)
                ttype = tt[0][2]
                qc.append(Query(name, oper, storage_manager.convert_to_value(value, ttype)))
            else:
                qc.append(q)
        return qc
