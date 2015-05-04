from __future__ import print_function

from graphene.commands.command import Command
from graphene.storage import StorageManager
from graphene.expressions import *
from graphene.traversal import *
from graphene.utils.conversion import TypeConversion
from graphene.errors import TypeMismatchException

import itertools

class InsertRelationCommand(Command):
    def __init__(self, ctx):
        self.rel, self.query1, self.query2 = ctx
        print("rel, query1, query2:", self.rel, self.query1, self.query2)

    def parse_properties(self, prop_list, schema, storage_manager):
        properties = []
        for prop, schema_tt in zip(prop_list, schema):
            tt, prop_name, exp_tt = schema_tt
            given_type = TypeConversion.get_type_type_of_string(prop)
            expected_type = exp_tt
            if given_type != expected_type:
                raise TypeMismatchException("Got value of type %s, but"
                            " expected value of type %s for property '%s'." %
                            (given_type, expected_type, prop_name))
            conv_value = storage_manager.convert_to_value(prop, given_type)
            properties.append((given_type, conv_value))
        return properties

    def execute(self, storage_manager):
        """
        Inserts a relationship into the storage layer.

        :type storage_manager: StorageManager
        :param storage_manager: storage manager for this instance
        :return: None
        """
        type1, queries1 = self.query1
        type2, queries2 = self.query2
        rel_name, rel_props = self.rel
        rel_type, rel_schema = storage_manager.get_relationship_data(rel_name)
        rel_props = self.parse_properties(rel_props, rel_schema, storage_manager)

        type_data1, type_schema_data1 = storage_manager.get_node_data(type1)
        type_data2, type_schema_data2 = storage_manager.get_node_data(type2)

        type_schema1 = [(tt_name, tt_type) for _, tt_name, tt_type in type_schema_data1]
        type_schema2 = [(tt_name, tt_type) for _, tt_name, tt_type in type_schema_data2]
        qc1 = Query.parse_chain(storage_manager, queries1, type_schema1)
        qc2 = Query.parse_chain(storage_manager, queries2, type_schema2)

        iter1 = NodeIterator(storage_manager, MatchNode(None, type1), type_schema1, queries=qc1)
        iter2 = NodeIterator(storage_manager, MatchNode(None, type2), type_schema2, queries=qc2)

        inserted_relations = []

        # Iterate over a product of the left node-set and right node-set. For
        # each, we will create a relation. We don't care if a node appears on
        # both sides; that's fine.
        for np1, np2 in itertools.product(iter1, iter2):
            if np1 == np2:
                continue

            print("Inserting relation %s between %s and %s" %
                (rel_name, np1.node, np2.node))
            rel = storage_manager.insert_relation(rel_type, rel_props, np1.node, np2.node)
            inserted_relations.append(rel)

        return inserted_relations
