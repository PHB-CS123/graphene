import unittest

from graphene.errors.storage_manager_errors import *
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.storage.intermediate import NodePropertyStore


class TestNodePropertyStore(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        self.sm = StorageManager()
        self.node_manager = self.sm.node_manager
        self.prop_manager = self.sm.property_manager
        self.nodeprop = NodePropertyStore(self.node_manager, self.prop_manager)
        self.type = self.sm.create_node_type("T", ())
        self.type_props = self.sm.create_node_type("R", (("a", "int"),))

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_node(self):
        idx = self.sm.insert_node(self.type, ())[0].index
        node, props = self.nodeprop[idx]
        self.assertEquals(len(props), 0)
        self.assertEquals(node, self.node_manager.get_item_at_index(idx))

    def test_node_with_props(self):
        idx = self.sm.insert_node(self.type_props,
                ((Property.PropertyType.int, 1),))[0].index
        node, props = self.nodeprop[idx]
        self.assertEquals(len(props), 1)
        self.assertEquals(node, self.node_manager.get_item_at_index(idx))

    def test_del_eof(self):
        with self.assertRaises(IndexError):
            del self.nodeprop[10]

    def test_del_twice(self):
        idx = self.sm.insert_node(self.type, ())[0].index
        node, props = self.nodeprop[idx]
        self.assertEquals(len(props), 0)
        self.assertEquals(node, self.node_manager.get_item_at_index(idx))
        del self.nodeprop[idx]
        self.assertEquals(self.nodeprop[idx], None)
        with self.assertRaises(KeyError):
            del self.nodeprop[idx]
