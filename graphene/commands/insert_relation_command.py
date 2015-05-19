from __future__ import print_function

from graphene.commands.command import Command
from graphene.storage import StorageManager
from graphene.expressions import *
from graphene.traversal import *
from graphene.utils.conversion import TypeConversion
from graphene.errors import TypeMismatchException, BadPropertyException

import itertools

class InsertRelationCommand(Command):
    def __init__(self, ctx):
        self.rel, self.query1, self.query2 = ctx

    def parse_properties(self, prop_list, schema, storage_manager):
        """
        Takes a list of properties that are intended to be inserted into the
        relation, check that they match the schema of the relation (in order),
        and then convert them to the desired type.

        :type prop_list: list
        :param prop_list: list of properties
        :type schema: list
        :param schema: list of tuples (type-type, property name, expected type)
        :type storage_manager: StorageManager
        :param storage_manager: storage manager for the calling instance
        :return: List of properties
        """
        properties = []
        schema_len = len(schema)
        num_props = len(prop_list)
        if num_props != schema_len:
            raise BadPropertyException("Expected %d propert%s, but got %d." % \
                (schema_len, "y" if schema_len == 1 else "ies", num_props))
        for prop, schema_tt in zip(prop_list, schema):
            tt, prop_name, exp_tt = schema_tt
            given_type = TypeConversion.get_type_type_of_string(prop)
            expected_type = exp_tt
            if given_type != expected_type:
                raise TypeMismatchException("Got value of type %s, but"
                            " expected value of type %s for property '%s'." %
                            (given_type, expected_type, prop_name))
            conv_value = TypeConversion.convert_to_value(prop, given_type)
            properties.append((given_type, conv_value))
        return properties

    def execute(self, storage_manager):
        """
        Inserts a relationship into the storage layer.

        :type storage_manager: StorageManager
        :param storage_manager: storage manager for this instance
        :return: List of inserted relations
        """
        # Gather information about the relation: name, type, schema and properties
        rel_name = self.rel[0]
        rel_type, rel_schema = storage_manager.get_relationship_data(rel_name)
        rel_props = self.parse_properties(self.rel[1] or [], rel_schema, storage_manager)

        # Determine type and schema information for type 1 (the left side of the
        # relation)
        type1, queries1 = self.query1
        type_data1, type_schema_data1 = storage_manager.get_node_data(type1)
        type_schema1 = [(tt_name, tt_type) for _, tt_name, tt_type in type_schema_data1]

        # Determine type and schema information for type 2 (the right side of the
        # relation)
        type2, queries2 = self.query2
        type_data2, type_schema_data2 = storage_manager.get_node_data(type2)
        type_schema2 = [(tt_name, tt_type) for _, tt_name, tt_type in type_schema_data2]

        # Parse queries for the left and right nodes
        qc1 = Query.parse_chain(storage_manager, queries1, type_schema1)
        qc2 = Query.parse_chain(storage_manager, queries2, type_schema2)

        # Create iterators for the left and right nodes
        iter1 = NodeIterator(storage_manager, MatchNode(None, type1), type_schema1, queries=qc1)
        iter2 = NodeIterator(storage_manager, MatchNode(None, type2), type_schema2, queries=qc2)

        inserted_relations = []

        # Iterate over a product of the left node-set and right node-set. For
        # each, we will create a relation. We don't care if a node appears on
        # both sides; that's fine.
        for np1, np2 in itertools.product(iter1, iter2):
            if np1 == np2:
                continue

            print("Inserting relation %s between %s and %s" % \
                (rel_name, np1.node, np2.node))
            rel = storage_manager.insert_relation(rel_type, rel_props,
                np1.node, np2.node)
            inserted_relations.append(rel)

        return inserted_relations
