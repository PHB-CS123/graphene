from graphene.commands.command import Command
from graphene.expressions import *
from graphene.traversal import Query
from graphene.query.planner import QueryPlanner

class DeleteRelationCommand(Command):
    """
    Used to delete individual relations from the database.
    """
    def __init__(self, data):
        self.rel_type = data.t
        self.qc = data.q
        self.left_node = data.nl
        self.right_node = data.nr

    def rel_iter(self, storage_manager, rel_data):
        """
        Iterates over relations based on a query if applicable.
        """
        rel_schema, rel_type, rel_query = rel_data
        for relprop in storage_manager.get_relations_of_type(rel_type):
            # Check that relation matches query if it exists
            if rel_query is not None:
                zipped = zip(rel_schema, relprop.properties)
                prop_dict = dict((sch[0], (value, sch[1])) for sch, value in zipped)
                if not rel_query.test(prop_dict):
                    continue

            yield relprop.rel

    def left_rel_iter(self, storage_manager, rel_data, node_data):
        """
        Iterates over relations with restrictions on the left side of the
        relation only.
        """
        rel_schema, rel_type, rel_query = rel_data
        node_schema, node_type, node_query = node_data
        # Iterate over the relations of the given type (and relation query)
        for rel in self.rel_iter(storage_manager, rel_data):
            left_nodeprop = storage_manager.get_node(rel.firstNodeId)
            left_node, left_props = left_nodeprop.node, left_nodeprop.properties
            # Check that left node matches desired type
            if left_node.nodeType != node_type.index:
                continue
            # Check that left node matches left query
            if node_query is not None:
                zipped = zip(node_schema, left_props)
                prop_dict = dict((sch[0], (value, sch[1])) for sch, value in zipped)
                if not node_query.test(prop_dict):
                    continue

            yield rel

    def right_rel_iter(self, storage_manager, rel_data, node_data):
        """
        Iterates over relations with restrictions on the right side of the
        relation only.
        """
        node_schema, node_type, node_query = node_data
        # Iterate over the relations of the given type (and relation query)
        for rel in self.rel_iter(storage_manager, rel_data):
            right_nodeprop = storage_manager.get_node(rel.secondNodeId)
            right_node, right_props = right_nodeprop.node, right_nodeprop.properties
            # Check that right node matches desired type
            if right_node.nodeType != node_type.index:
                continue
            # Check that right node matches right query
            if node_query is not None:
                zipped = zip(node_schema, right_props)
                prop_dict = dict((sch[0], (value, sch[1])) for sch, value in zipped)
                if not node_query.test(prop_dict):
                    continue
            yield rel

    def both_rel_iter(self, storage_manager, rel_data, left_data, right_data):
        """
        Iterates over relations with restrictions on both sides of the relation.

        Effectively iterates on the left and then on the right.
        """
        node_schema, node_type, node_query = right_data
        # Iterate over relation + left node
        for rel in self.left_rel_iter(storage_manager, rel_data, left_data):
            right_nodeprop = storage_manager.get_node(rel.secondNodeId)
            right_node, right_props = right_nodeprop.node, right_nodeprop.properties
            # Check that right node matches desired type
            if right_node.nodeType != node_type.index:
                continue
            # Check that right node matches right query
            if node_query is not None:
                zipped = zip(node_schema, right_props)
                prop_dict = dict((sch[0], (value, sch[1])) for sch, value in zipped)
                if not node_query.test(prop_dict):
                    continue
            yield rel

    def execute(self, storage_manager):
        planner = QueryPlanner(storage_manager)
        # Get information about relation itself
        rel_schema = planner.get_schema([MatchRelation(None, self.rel_type)])
        schema_names = map(lambda p: p[0], rel_schema)
        q = Query.parse_chain(storage_manager, self.qc, rel_schema)
        rel_type, schema = storage_manager.get_relationship_data(self.rel_type)
        rel_data = (rel_schema, rel_type, q)

        left_data, right_data = None, None
        # If the left node was specified, gather information about the left node
        if self.left_node is not None:
            left_type, left_qc = self.left_node
            node_schema = planner.get_schema([MatchNode(None, left_type)])
            node_type, _ = storage_manager.get_node_data(left_type)
            if len(left_qc) > 0:
                node_query = Query.parse_chain(storage_manager, left_qc, node_schema)
            else:
                node_query = None
            left_data = (node_schema, node_type, node_query)
        # If the right node was specified, gather information about the right node
        if self.right_node is not None:
            right_type, right_qc = self.right_node
            node_schema = planner.get_schema([MatchNode(None, right_type)])
            node_type, _ = storage_manager.get_node_data(right_type)
            if len(right_qc) > 0:
                node_query = Query.parse_chain(storage_manager, right_qc, node_schema)
            else:
                node_query = None
            right_data = (node_schema, node_type, node_query)

        # Determine the correct iterator to use
        if left_data is not None and right_data is not None:
            rel_iter = self.both_rel_iter(storage_manager, rel_data, left_data, right_data)
        elif left_data is not None:
            rel_iter = self.left_rel_iter(storage_manager, rel_data, left_data)
        elif right_data is not None:
            rel_iter = self.right_rel_iter(storage_manager, rel_data, right_data)
        else:
            rel_iter = self.rel_iter(storage_manager, rel_data)

        # Delete relations yielded by generator
        for rel in rel_iter:
            del storage_manager.relprop[rel.index]
