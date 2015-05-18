from graphene.traversal.query import Query
from graphene.traversal.node_iterator import NodeIterator
from graphene.storage import *
from graphene.expressions import *

class RelationIterator:
    def __init__(self, storage_manager, match_rel, left_child, right_child, schema):
        self.sm = storage_manager
        self.alias = match_rel.name
        self.type_name = match_rel.type
        self.rel_type, self.type_schema = storage_manager.get_relationship_data(self.type_name)
        # Queries that apply to the entire chunk but not specific children. This
        # basically will only be queries that are ORs with schemas overlapping
        # over parts of this iteration
        self.queries = None
        # Queries that apply only to the relationship (as if we were doing a
        # node iterator on the relationship)
        self.rel_queries = None
        self.left = left_child
        self.right = right_child

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

    def __repr__(self):
        if self.alias is not None:
            key = "%s:%s" % (self.alias, self.type_name)
        else:
            key = self.type_name
        if self.rel_queries is not None:
            s = "RelationIterator[%s, %s: %s, %s]" % (self.left, key, self.rel_queries, self.right)
        else:
            s = "RelationIterator[%s, %s, %s]" % (self.left, key, self.right)
        if self.queries is not None:
            s += "[%s]" % self.queries
        return s

    def get_rel_schema(self):
        """
        Generate the schema for the relation
        """
        if self.alias is not None:
            return set("%s.%s" % (self.alias, tname) for tt, tname, ttype in self.type_schema)
        else:
            return set(tname for tt, tname, ttype in self.type_schema)

    @property
    def schema(self):
        """
        Generate the schema for the relation iterator. Combines the relation
        schema with the schemas of the left and right children.
        """
        return (self.get_rel_schema() | self.left.schema | self.right.schema)

    def add_query(self, query):
        """
        Adds a query to the current list of queries. Since ORs are not able to
        be split, "adding" a query consists of ANDing it with whatever was there
        before.
        """
        # If it's part of the relation schema, add to the relation queries
        if query.schema <= self.get_rel_schema():
            # Nothing there, so just replace
            if self.rel_queries is None:
                self.rel_queries = query
            # Not an AndOperator, so create a new one
            elif isinstance(self.rel_queries, Query) \
                    or isinstance(self.rel_queries, OrOperator):
                self.rel_queries = AndOperator([self.rel_queries, query])
            # AndOperator, so just tack on the query
            elif isinstance(self.rel_queries, AndOperator):
                self.rel_queries.children.append(query)
        else:
            if query.schema <= self.left.schema:
                self.left.add_query(query)
            elif query.schema <= self.right.schema:
                self.right.add_query(query)
            else:
                # Do the same thing with our overall queries, since it applies
                # to some subset of the entire schema
                if self.queries is None:
                    self.queries = query
                # Not an AndOperator, so create a new one
                elif isinstance(self.queries, Query) \
                        or isinstance(self.queries, OrOperator):
                    self.queries = AndOperator([self.queries, query])
                # AndOperator, so just tack on the query
                elif isinstance(self.queries, AndOperator):
                    self.queries.children.append(query)


    def __iter__(self):
        for relprop in self.sm.get_relations_of_type(self.rel_type):
            rel = relprop.rel
            # Make sure relation matches queries provided
            if isinstance(self.queries, Query):
                if not self.queries.test(self.prop_to_dict(relprop.properties)):
                    continue

            # Right side will always be a NodeIterator (we branch to the left)
            right_node = self.sm.get_node(rel.secondNodeId)
            left_node = self.sm.get_node(rel.firstNodeId)

            # If the right node is not of the correct type or wasn't matched by
            # the right side's iteration, then this doesn't match
            if right_node.node.nodeType != self.right.node_type.index \
                or not self.right.node_matches(right_node.properties):
                continue

            # If the left is a NodeIterator, our original request was one degree
            # of separation
            if isinstance(self.left, NodeIterator):
                # Check the left node's type
                if left_node.node.nodeType != self.left.node_type.index:
                    continue
                # Check that the left node existed in the left result iterator.
                # If it did, return properties and the right node (so that
                # future chains can determine whether their left node
                # corresponds to this right node)
                if self.left.node_matches(left_node.properties):
                    yield (left_node.properties + relprop.properties + \
                            right_node.properties, right_node)
            # Otherwise, we already chained from something else, so we just
            # check that the left node is the right node of something on the
            # left side of the iteration
            else:
                for props, right in self.left:
                    if left_node.node == right.node:
                        yield (props + relprop.properties + \
                                right_node.properties, right_node)
