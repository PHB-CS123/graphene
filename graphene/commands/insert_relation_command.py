from __future__ import print_function

from graphene.commands.command import Command
from graphene.storage import StorageManager
from graphene.traversal import *
from graphene.utils.conversion import TypeConversion
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
                raise Exception("Got value of type %s, but expected value "
                                "of type %s for property '%s'." %
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
        from pdb import set_trace
        type1, queries1 = self.query1
        type2, queries2 = self.query2
        rel_name, rel_props = self.rel
        rel_type, rel_schema = storage_manager.get_relationship_data(rel_name)
        rel_props = self.parse_properties(rel_props, rel_schema, storage_manager)

        print(rel_props)

        type_data1, type_schema1 = storage_manager.get_node_data(type1)
        type_data2, type_schema2 = storage_manager.get_node_data(type2)

        qc1 = Query.parse_chain(storage_manager, queries1, type_schema1)
        qc2 = Query.parse_chain(storage_manager, queries2, type_schema2)

        iter1 = NodeIterator(storage_manager, type_data1, type_schema1, queries=qc1)
        iter2 = NodeIterator(storage_manager, type_data2, type_schema2, queries=qc2)

        # final_rel_props = []
        # for prop, schema_tt in zip(rel_props, rel_schema):
        #     tt, prop_name, exp_tt = schema_tt
        #     given_type = TypeCxpected_type:
        #         raise Exception("Got value of type %s, but expected value "
        #                      onversion.get_type_type_of_string(prop)
        #     expected_type = exp
        # set_trace()_tt
        #     if given_type != e   "of type %s for property '%s'." %
        #                         (given_type, expected_type, prop_name))
        #     conv_value = storage_manager.convert_to_value(prop, given_type)
        #     final_rel_props.append((given_type, conv_value))
        #

        for node1, node2 in itertools.product(iter1, iter2):
            if node1 == node2:
                continue
            print(node1, node2)
            set_trace()
            storage_manager.insert_relation(rel_type, rel_props, node1, node2)
