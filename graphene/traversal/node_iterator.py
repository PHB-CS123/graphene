from graphene.traversal.query import Query
from graphene.expressions import AndOperator, OrOperator
from graphene.storage import *

class NodeIterator:
    def __init__(self, storage_manager, match_node, schema, queries=None):
        self.sm = storage_manager
        self.alias = match_node.name
        self.type_name = match_node.type
        self.node_type, self.type_schema = storage_manager.get_node_data(match_node.type)
        # copy to ensure tuple in argument default is not modified
        self.queries = queries

    def __repr__(self):
        if self.alias is not None:
            key = "%s:%s" % (self.alias, self.type_name)
        else:
            key = self.type_name
        if self.queries is not None:
            return "NodeIterator[%s: %s]" % (key, self.queries)
        else:
            return "NodeIterator[%s]" % key

    @property
    def schema(self):
        """
        Generate the schema for the node iterator
        """
        schema = set(tname for tt, tname, ttype in self.type_schema)
        if self.alias is not None:
            schema = schema | set("%s.%s" % (self.alias, tname) for tt, tname, ttype in self.type_schema)
        return schema

    def add_query(self, query):
        """
        Adds a query to the current list of queries. Since ORs are not able to
        be split, "adding" a query consists of ANDing it with whatever was there
        before.
        """
        # We can only AND queries together, since ORing is not pushable down
        if query.schema <= self.schema:
            # Nothing there, so just replace
            if self.queries is None:
                self.queries = query
            # Not an AndOperator, so create a new one
            elif isinstance(self.queries, Query) or isinstance(self.queries, OrOperator):
                self.queries = AndOperator([self.queries, query])
            # AndOperator, so just tack on the query
            elif isinstance(self.queries, AndOperator):
                self.queries.children.append(query)

    def prop_to_dict(self, props):
        """
        Converts the provided property list into a dict corresponding to the key
        names (which may have identifiers)
        """
        result = {}
        for i, tt_data in enumerate(self.type_schema):
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
        if self.queries is None:
            return True
        else:
            return self.queries.test(self.prop_to_dict(properties))

    def __iter__(self):
        for nodeprop in self.sm.get_nodes_of_type(self.node_type):
            if self.node_matches(nodeprop.properties):
                yield nodeprop
