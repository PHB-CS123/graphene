class Query:
    def __init__(self, ident, name, oper, value):
        self.ident = ident
        self.name = name
        self.oper = oper
        self.value = value

    def test(self, prop_dict):
        if self.ident is not None:
            key = "%s.%s" % (self.ident, self.name)
        else:
            key = self.name
        try:
            value, tt = prop_dict[key]
        except KeyError:
            raise Exception("%s is not a valid property name." % key)
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

    def __repr__(self):
        if self.ident is not None:
            return "Query[%s.%s %s %s]" % (self.ident, self.name, self.oper, self.value)
        else:
            return "Query[%s %s %s]" % (self.name, self.oper, self.value)

    @staticmethod
    def parse_chain(storage_manager, chain, type_schema):
        qc = []
        for q in chain:
            if type(q) == tuple:
                # actual query
                ident, name, oper, value = q
                tt = filter(lambda t: t[0] == name or t[0].split(".")[1] == name, type_schema)
                if len(tt) == 0:
                    # no such named property
                    raise Exception("%s is not a valid property name." % name)
                ttype = tt[0][1]
                qc.append(Query(ident, name, oper, storage_manager.convert_to_value(value, ttype)))
            else:
                qc.append(q)
        return qc
