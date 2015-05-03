import unittest

from graphene.errors.storage_manager_errors import *
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.storage.intermediate import RelationshipPropertyStore


class TestNodePropertyStore(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        self.sm = StorageManager()
        self.relationship_manager = self.sm.relationship_manager
        self.prop_manager = self.sm.property_manager
        self.relprop = RelationshipPropertyStore(self.relationship_manager, self.prop_manager)
        self.type = self.sm.create_relationship_type("RA", ())
        self.type_props = self.sm.create_relationship_type("RB", (("a", "int"),))

        node_type = self.sm.create_node_type("T", (("a", "int"),))
        self.n1, self.p1 = self.sm.insert_node(node_type, ((Property.PropertyType.int, 1),))
        self.n2, self.p2 = self.sm.insert_node(node_type, ((Property.PropertyType.int, 2),))

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_relation(self):
        idx = self.sm.insert_relation(self.type, (), self.n1, self.n2).index
        rel, props = self.relprop[idx]
        self.assertEquals(len(props), 0)
        self.assertEquals(rel, self.relationship_manager.get_item_at_index(idx))

    def test_relation_with_props(self):
        idx = self.sm.insert_relation(self.type_props,
                ((Property.PropertyType.int, 1),), self.n1, self.n2).index
        rel, props = self.relprop[idx]
        self.assertEquals(len(props), 1)
        self.assertEquals(rel, self.relationship_manager.get_item_at_index(idx))

    def test_del_eof(self):
        with self.assertRaises(IndexError):
            del self.relprop[10]

    def test_del(self):
        idx = self.sm.insert_relation(self.type_props,
                ((Property.PropertyType.int, 1),), self.n1, self.n2).index
        del self.relprop[idx]


    def test_del_twice(self):
        idx = self.sm.insert_relation(self.type, (), self.n1, self.n2).index
        node, props = self.relprop[idx]
        self.assertEquals(len(props), 0)
        self.assertEquals(node, self.relationship_manager.get_item_at_index(idx))
        del self.relprop[idx]
        self.assertEquals(self.relprop[idx], None)
        with self.assertRaises(KeyError):
            del self.relprop[idx]
