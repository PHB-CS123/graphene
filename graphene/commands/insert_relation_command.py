from graphene.commands.command import Command
from graphene.storage import Property
from graphene.traversal import *
import itertools

class InsertRelationCommand(Command):
    def __init__(self, ctx):
        self.rel, self.query1, self.query2 = ctx

    def execute(self, storage_manager):
        type1, queries1 = self.query1
        type2, queries2 = self.query2
        rel_type, rel_queries = self.rel
        type_data1, type_schema1 = storage_manager.get_node_data(type1)
        type_data2, type_schema2 = storage_manager.get_node_data(type2)

        qc1 = Query.parse_chain(storage_manager, queries1, type_schema1)
        qc2 = Query.parse_chain(storage_manager, queries2, type_schema2)

        iter1 = NodeIterator(storage_manager, type_data1, type_schema1, qc1)
        iter2 = NodeIterator(storage_manager, type_data2, type_schema2, qc2)

        for node1, node2 in itertools.product(iter1, iter2):
            if node1 == node2:
                continue
            print node1, node2
