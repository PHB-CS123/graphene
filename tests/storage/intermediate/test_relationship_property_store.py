import unittest

from graphene.errors.storage_manager_errors import *
from graphene.storage import StorageManager
from graphene.storage.base.general_store import *
from graphene.storage.base.property import Property
from graphene.storage.intermediate import RelationshipPropertyStore


class TestRelationshipPropertyStore(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        self.sm = StorageManager()
        self.relationship_manager = self.sm.relationship_manager
        self.prop_manager = self.sm.property_manager
        self.relprop = RelationshipPropertyStore(self.sm)
        self.type = self.sm.create_relationship_type("RA", ())
        self.type_props = self.sm.create_relationship_type("RB", (("a", "int"),))

        node_type = self.sm.create_node_type("T", (("a", "int"),))
        self.n1, self.p1 = \
            self.sm.insert_node(node_type, ((Property.PropertyType.int, 1),))
        self.n2, self.p2 = \
            self.sm.insert_node(node_type, ((Property.PropertyType.int, 2),))
        self.n3, self.p3 = \
            self.sm.insert_node(node_type, ((Property.PropertyType.int, 3),))

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        self.sm.close()

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
        # Write two items to the relationship-property store
        idx = self.sm.insert_relation(self.type, (), self.n1, self.n2).index
        idx2 = self.sm.insert_relation(self.type, (), self.n1, self.n3).index

        # Make sure the data is as expected
        node, props = self.relprop[idx]
        self.assertEquals(len(props), 0)
        self.assertEquals(node,
                          self.relationship_manager.get_item_at_index(idx))
        node2, props2 = self.relprop[idx2]
        self.assertEquals(len(props2), 0)
        self.assertEquals(node2,
                          self.relationship_manager.get_item_at_index(idx2))

        # Delete the first created item
        del self.relprop[idx]
        self.assertEquals(self.relprop[idx], None)
        with self.assertRaises(KeyError):
            del self.relprop[idx]

        # Delete the second created item, should be at the end of the file
        del self.relprop[idx2]
        self.assertEquals(self.relprop[idx2], EOF)
        with self.assertRaises(IndexError):
            del self.relprop[idx2]
