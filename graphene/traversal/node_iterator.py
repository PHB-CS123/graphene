from graphene.traversal.query import Query
from graphene.storage import *

class NodeIterator:
    def __init__(self, storage_manager, node_type, type_schema, alias=None, queries=None):
        self.sm = storage_manager
        self.node_type = node_type
        self.schema = type_schema
        self.alias = alias
        if queries is not None:
            self.queries = queries
        else:
            self.queries = ()

    def prop_to_dict(self, props):
        result = {}
        for i, tt_data in enumerate(self.schema):
            tt, name, tt_type = tt_data
            # If there is an alias, create a key from it; i.e. if the type
            # identifier is t, then t.a works.

            # TODO: Handle multiple scenarios with multiple aliases; also notice
            # duplicates
            if self.alias is not None:
                key = "%s.%s" % (self.alias, name)
            else:
                key = name
            result[key] = (props[i], tt_type)
        return result

    def __iter__(self):
        for node in self.sm.get_nodes_of_type(self.node_type):
            # For now we assume all the queries are ANDed together.
            # TODO: Handle actual boolean logic. Probably will involve some
            # recursion somewhere.
            matches = True
            for q in self.queries:
                if isinstance(q, Query):
                    matches = matches and q.test(self.prop_to_dict(node.properties))
            if matches:
                yield node
