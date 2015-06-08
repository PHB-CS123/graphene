from graphene.errors import *
from graphene.utils.conversion import TypeConversion
from graphene.storage import Property
from graphene.expressions import AndOperator, OrOperator

# Group a list based on a delimiter.
# Adapted from http://stackoverflow.com/a/15358005/28429
def group(seq, sep):
    g = []
    for el in seq:
        if el == sep:
            yield g
            g = []
        else:
            g.append(el)
    yield g

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
        if type(self.value) is tuple:
            if self.value[0] is not None:
                key_right = "%s.%s" % self.value
            else:
                key_right = self.value[1]
            try:
                given_value, tt_right = prop_dict[key_right]
            except KeyError:
                raise NonexistentPropertyException("%s is not a valid property name." % key_right)
        else:
            given_value = self.value
        if self.oper == '=':
            return value == given_value
        if self.oper == '!=':
            return value != given_value
        if self.oper == '>=':
            return value >= given_value
        if self.oper == '>':
            return value > given_value
        if self.oper == '<=':
            return value <= given_value
        if self.oper == '<':
            return value < given_value
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

    @property
    def schema(self):
        if self.ident is not None:
            s = set(["%s.%s" % (self.ident, self.name)])
        else:
            s = set([self.name])

        # right side is a name, so add that
        if type(self.value) is tuple:
            if self.value[0] is not None:
                s.add("%s.%s" % self.value)
            else:
                s.add(self.value[1])

        return s

    def apply_to(self, tree):
        # if this schema is a subset of the tree schema, we can just apply it
        if self.schema <= tree.schema:
            tree.add_query(self)

    @staticmethod
    def reduce_operators(chain):
        """
        Turns a nested list with boolean operators as strings into one with
        actual operator instances.
        """
        if isinstance(chain, Query) or isinstance(chain, AndOperator) or \
            isinstance(chain, OrOperator):
            # Just a query value, so return it
            return chain
        elif chain.count("OR") > 0:
            # There's ORs, and these have less precedence, so separate them
            # first
            return OrOperator(map(Query.reduce_operators, group(chain, "OR")))
        elif chain.count("AND") > 0:
            # Otherwise, separate the ANDs (idea is these guys are closer
            # together)
            return AndOperator(map(Query.reduce_operators, group(chain, "AND")))
        elif chain == []:
            # Empty list
            return []
        else:
            # Otherwise we have a list with an extra list around it, so just
            # recurse
            return Query.reduce_operators(chain[0])

    @staticmethod
    def parse_chain(storage_manager, chain, type_schema):
        """
        Parses a chain of queries from tuples of basic information (i.e. the
        identifier, name of the property, the operator, and the value tested)
        given the schema they should apply to. Returns a list of Query objects
        that can be used for testing later.
        """
        if chain is None:
            # Nothing to parse
            return None
        # Parse a series of parentheses in to a nested list, e.g.
        # 1(23(45)(6)) turns into [1, [2, 3, [4, 5], [6]]]
        # Adapted from http://stackoverflow.com/a/17141899/28429
        qc = [[]]
        for q in chain:
            if type(q) == tuple:
                # actual query
                left, oper, value = q
                ident, name = left
                # check that the named property exists
                # TODO: Check if this is actually correct...
                tt = filter(lambda t: t[0] == name or t[0].split(".")[-1] == name, type_schema)
                if len(tt) == 0:
                    raise NonexistentPropertyException("%s is not a valid property name." % name)
                ttype = tt[0][1]
                # If the value is actually another property, we can't know since
                # it might be another schema
                if type(value) is not tuple:
                    if value == "[]":
                        if ttype.value < Property.PropertyType.intArray.value:
                            raise TypeMismatchException("Got empty array, but " \
                                    "expected value of type %s for property '%s'." \
                                    % (ttype, name))
                        else:
                            converted_value = []
                    else:
                        value_type = TypeConversion.get_type_type_of_string(value)
                        if value_type != ttype:
                            raise TypeMismatchException("Got value of type %s, " \
                                "but expected value of type %s for property '%s'." \
                                 % (value_type, ttype, name))
                        else:
                            converted_value = TypeConversion.convert_to_value(value, ttype)
                    qc[-1].append(Query(ident, name, oper, converted_value))
                else:
                    qc[-1].append(Query(ident, name, oper, value))
            elif q == '(':
                qc[-1].append([])
                qc.append(qc[-1][-1])
            elif q == ')':
                qc.pop()
                if not qc:
                    # TODO: These should be a SyntaxError from the parser, sorta
                    raise ValueError('error: opening bracket is missing')
            else:
                qc[-1].append(q.upper()) # operators are assumed to be uppercase
        if len(qc) > 1:
            # TODO: These should be a SyntaxError from the parser, sorta
            raise ValueError('error: closing bracket is missing')
        qc = qc.pop()
        return Query.reduce_operators(qc)
