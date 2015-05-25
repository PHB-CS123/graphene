import unittest

from graphene.errors.storage_manager_errors import *
from graphene.storage import StorageManager
from graphene.storage.base.general_store import *
from graphene.storage.base.property import Property
from graphene.storage.intermediate import NodePropertyStore


class TestNodePropertyStore(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        self.sm = StorageManager()
        self.node_manager = self.sm.node_manager
        self.prop_manager = self.sm.property_manager
        self.prop_string_manager = self.sm.prop_string_manager
        self.array_manager = self.sm.array_manager
        self.nodeprop = NodePropertyStore(self.node_manager, self.prop_manager,
            self.prop_string_manager, self.array_manager)
        self.type = self.sm.create_node_type("T", ())
        self.type_props = self.sm.create_node_type("R", (("a", "int"),))

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        del self.sm
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
        # Write two items to the node-property store
        idx = self.sm.insert_node(self.type, ())[0].index
        idx2 = self.sm.insert_node(self.type, ())[0].index

        # Make sure the data is as expected
        node, props = self.nodeprop[idx]
        self.assertEquals(len(props), 0)
        self.assertEquals(node, self.node_manager.get_item_at_index(idx))
        node2, props2 = self.nodeprop[idx2]
        self.assertEquals(len(props2), 0)
        self.assertEquals(node2, self.node_manager.get_item_at_index(idx2))

        # Delete the first created item
        del self.nodeprop[idx]
        self.assertEquals(self.nodeprop[idx], None)
        # Check that a KeyError is raised when another delete is attempted
        with self.assertRaises(KeyError):
            del self.nodeprop[idx]

        # Delete the second created item, should be at the end of the file
        del self.nodeprop[idx2]
        self.assertEquals(self.nodeprop[idx2], EOF)
        with self.assertRaises(IndexError):
            del self.nodeprop[idx2]
