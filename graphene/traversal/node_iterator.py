from graphene.traversal.query import Query
from graphene.storage import *

class NodeIterator:
    def __init__(self, storage_manager, match_node, schema, queries=()):
        self.sm = storage_manager
        self.alias = match_node.name
        self.node_type, self.schema = storage_manager.get_node_data(match_node.type)
        # copy to ensure tuple in argument default is not modified
        self.queries = queries[:]

    def prop_to_dict(self, props):
        """
        Converts the provided property list into a dict corresponding to the key
        names (which may have identifiers)
        """
        result = {}
        for i, tt_data in enumerate(self.schema):
            tt, name, tt_type = tt_data
            # If there is an alias, create a key from it; i.e. if the type
            # identifier is t, then t.a works.

            # TODO: Handle multiple scenarios with multiple aliases; also notice
            # duplicates
            if self.alias is not None:
                key = "%s.%s" % (self.alias, name)
                result[key] = (props[i], tt_type)
            result[name] = (props[i], tt_type)
        return result

    def node_matches(self, properties):
        """
        Tests whether the provided properties (which came from a node) are
        matched by the queries the iterator was provided with.
        """
        # For now we assume all the queries are ANDed together.
        # TODO: Handle actual boolean logic. Probably will involve some
        # recursion somewhere.
        matches = True
        for q in self.queries:
            if isinstance(q, Query):
                matches = matches and q.test(self.prop_to_dict(properties))
        return matches

    def __iter__(self):
        for nodeprop in self.sm.get_nodes_of_type(self.node_type):
            if self.node_matches(nodeprop.properties):
                yield nodeprop
