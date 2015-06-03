from graphene.commands.command import Command
from graphene.expressions import *
from graphene.traversal import Query
from graphene.query.planner import QueryPlanner

class RelationIterator(Command):
    """
    Used to iterate through relations in the database.
    """
    def __init__(self, rel_type, query_chain, left_node, right_node):
        self.rel_type = rel_type
        self.qc = query_chain
        self.left_node = left_node
        self.right_node = right_node

    def get_prop_dict(self, schema, properties):
        """
        Given a schema (with structure [(name, type)]) and a set of properties,
        create the dict with keys as the names and values with structure
        (property_value, type).
        """
        # Zip these together so that the property information is combined with
        # the property value
        zipped = zip(schema, properties)
        return dict((sch[0], (value, sch[1])) for sch, value in zipped)

    def rel_iter(self, storage_manager, rel_data):
        """
        Iterates over relations based on a query if applicable.
        """
        rel_schema, rel_type, rel_query = rel_data
        for relprop in storage_manager.get_relations_of_type(rel_type):
            # Check that relation matches query if it exists
            if rel_query is not None:
                prop_dict = self.get_prop_dict(rel_schema, relprop.properties)
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
                prop_dict = self.get_prop_dict(node_schema, left_props)
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
                prop_dict = self.get_prop_dict(node_schema, right_props)
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
                prop_dict = self.get_prop_dict(node_schema, right_props)
                if not node_query.test(prop_dict):
                    continue
            yield rel

    def execute(self, storage_manager):
        """
        Determines the proper iterator to use based on the query

        :param storage_manager: Storage manager to obtain data from
        :type storage_manager: StorageManager
        :return: Relation iterator to use for delete or update (generator)
        :rtype: list[Relationship]
        """
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
            if left_qc is not None and len(left_qc) > 0:
                node_query = Query.parse_chain(storage_manager, left_qc, node_schema)
            else:
                node_query = None
            left_data = (node_schema, node_type, node_query)
        # If the right node was specified, gather information about the right node
        if self.right_node is not None:
            right_type, right_qc = self.right_node
            node_schema = planner.get_schema([MatchNode(None, right_type)])
            node_type, _ = storage_manager.get_node_data(right_type)
            if right_qc is not None and len(right_qc) > 0:
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

        return rel_iter
