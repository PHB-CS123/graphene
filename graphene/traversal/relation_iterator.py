from graphene.traversal.query import Query
from graphene.traversal.node_iterator import NodeIterator
from graphene.storage import *

class RelationIterator:
    def __init__(self, storage_manager, match_rel, left_child, right_child, schema, queries=None):
        self.sm = storage_manager
        self.alias = match_rel.name
        self.rel_type, self.schema = storage_manager.get_relationship_data(match_rel.type)
        #self.schema = schema
        if queries is not None:
            self.queries = queries
        else:
            self.queries = ()
        self.left = left_child
        self.right = right_child

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
                result[key] = (props[i], tt_type)
            result[name] = (props[i], tt_type)
        return result

    def __iter__(self):
        for relprop in self.sm.get_relations_of_type(self.rel_type):
            rel = relprop.rel
            # Make sure relation matches queries provided
            matches = True
            for q in self.queries:
                if isinstance(q, Query):
                    matches = matches and q.test(self.prop_to_dict(relprop.properties))
            if not matches:
                continue

            # Right side will always be a NodeIterator (we branch to the left)
            right_node = self.sm.get_node(rel.secondNodeId)
            left_node = self.sm.get_node(rel.firstNodeId)

            # If the right node is not of the correct type or wasn't matched by
            # the right side's iteration, then this doesn't match
            if right_node.node.nodeType != self.right.node_type.index \
                or right_node not in self.right:
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
                if left_node in self.left:
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
