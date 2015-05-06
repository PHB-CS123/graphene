from graphene.errors import *

class Query:
    def __init__(self, ident, name, oper, value):
        self.ident = ident
        self.name = name
        self.oper = oper
        self.value = value

    def test(self, prop_dict):
        """
        Test the current query against a dictionary of properties, which
        correspond to some node we are trying to match with.
        """
        if self.ident is not None:
            key = "%s.%s" % (self.ident, self.name)
        else:
            key = self.name
        try:
            value, tt = prop_dict[key]
        except KeyError:
            raise NonexistentPropertyException("%s is not a valid property name." % key)
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
        # TODO: This should probably throw an error...
        return False

    def __repr__(self):
        if self.ident is not None:
            return "Query[%s.%s %s %s]" % (self.ident, self.name, self.oper, self.value)
        else:
            return "Query[%s %s %s]" % (self.name, self.oper, self.value)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.ident == other.ident) and \
                   (self.name == other.name) and \
                   (self.oper == other.oper) and \
                   (self.value == other.value)
        else:
            return False

    def __ne__(self, other):
        return not (self == other)

    @staticmethod
    def parse_chain(storage_manager, chain, type_schema):
        """
        Parses a chain of queries from tuples of basic information (i.e. the
        identifier, name of the property, the operator, and the value tested)
        given the schema they should apply to. Returns a list of Query objects
        that can be used for testing later.
        """
        qc = []
        for q in chain:
            if type(q) == tuple:
                # actual query
                ident, name, oper, value = q
                # check that the named property exists
                # TODO: Check if this is actually correct...
                tt = filter(lambda t: t[0] == name or t[0].split(".")[-1] == name, type_schema)
                if len(tt) == 0:
                    raise NonexistentPropertyException("%s is not a valid property name." % name)
                ttype = tt[0][1]
                qc.append(Query(ident, name, oper, storage_manager.convert_to_value(value, ttype)))
            else:
                qc.append(q)
        return qc
