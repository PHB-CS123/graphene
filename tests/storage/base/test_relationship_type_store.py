import unittest

from graphene.storage.base.relationship_type_store import *


class TestRelationshipTypeStoreMethods(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_empty_init(self):
        """
        Test that initializing an empty RelationshipTypeStore succeeds
        (file is opened)
        """
        try:
            RelationshipType()
        except IOError:
            self.fail("RelationshipTypeStore initializer failed: "
                      "db file failed to open.")

    def test_double_init(self):
        """
        Test that initializing an empty RelationshipTypeStore succeeds when
        repeated; i.e. the old file is reopened and no errors occur.
        """
        try:
            RelationshipTypeStore()
        except IOError:
            self.fail("RelationshipTypeStore initializer failed: "
                      "db file failed to open.")
        try:
            RelationshipTypeStore()
        except IOError:
            self.fail("RelationshipTypeStore initializer failed "
                      "on second attempt: db file failed to open.")

    def test_invalid_write(self):
        """
        Test that writing a relationship type to index 0 raises an error
        """
        relationship_type_store = RelationshipTypeStore()

        empty_relationship_type = RelationshipType()
        with self.assertRaises(ValueError):
            relationship_type_store.write_item(empty_relationship_type)

    def test_invalid_read(self):
        """
        Test that reading a relationship type from index 0 raises an error
        """
        relationship_type_store = RelationshipTypeStore()

        with self.assertRaises(ValueError):
            relationship_type_store.item_at_index(0)

    def test_empty_read(self):
        """
        Make sure that reading an item when the file is empty returns None
        """
        relationship_type_store = RelationshipTypeStore()
        # Read an uncreated item
        no_item = relationship_type_store.item_at_index(1)
        # Make sure it returned None
        self.assertEquals(no_item, None)

    def test_write_read_1_relationship_type(self):
        """
        Tests that the node written to the NodeStore is the node that is read.
        """
        relationship_type_store = RelationshipTypeStore()

        # Create a node and add it to the NodeStore
        rel_type = RelationshipType(1, False, 1)
        relationship_type_store.write_item(rel_type)

        # Read the node from the NodeStore file
        rel_type_file = relationship_type_store.item_at_index(rel_type.index)

        # Assert that the values are the same
        self.assertEquals(rel_type, rel_type_file)

    def test_write_read_2_relationship_types(self):
        """
        Tests when 2 nodes are written after 1 node to the NodeStore
        """
        relationship_type_store = RelationshipTypeStore()

        # Create one node and write it to the NodeStore
        rel_type1 = RelationshipType(1, False, 1)
        relationship_type_store.write_item(rel_type1)

        # Create 2 nodes and add them to the NodeStore
        rel_type2 = RelationshipType(2, False, 2)
        rel_type3 = RelationshipType(3, False, 3)
        relationship_type_store.write_item(rel_type2)
        relationship_type_store.write_item(rel_type3)

        # Read the nodes from the NodeStore file
        rel_type1_file = relationship_type_store.item_at_index(rel_type1.index)
        rel_type2_file = relationship_type_store.item_at_index(rel_type2.index)
        rel_type3_file = relationship_type_store.item_at_index(rel_type3.index)

        # Make sure their values are the same
        self.assertEquals(rel_type1, rel_type1_file)
        self.assertEquals(rel_type2, rel_type2_file)
        self.assertEquals(rel_type3, rel_type3_file)

    def test_overwrite_relationship_type(self):
        """
        Tests that overwriting a node in a database with 3 nodes works
        """
        relationship_type_store = RelationshipTypeStore()

        # Create 3 nodes
        rel_type1 = RelationshipType(1, False, 1)
        rel_type2 = RelationshipType(2, False, 2)
        rel_type3 = RelationshipType(3, False, 3)

        # Write them to the nodestore
        relationship_type_store.write_item(rel_type1)
        relationship_type_store.write_item(rel_type2)
        relationship_type_store.write_item(rel_type3)

        # Verify that they are in the store as expected
        rel_type1_file = relationship_type_store.item_at_index(rel_type1.index)
        self.assertEquals(rel_type1, rel_type1_file)

        rel_type2_file = relationship_type_store.item_at_index(rel_type2.index)
        self.assertEquals(rel_type2, rel_type2_file)

        rel_type3_file = relationship_type_store.item_at_index(rel_type3.index)
        self.assertEquals(rel_type3, rel_type3_file)

        # Create a new rel_type2 and overwrite the old rel_type2
        new_rel_type2 = RelationshipType(2, True, 8)
        relationship_type_store.write_item(new_rel_type2)

        # Verify that the data is still as expected
        rel_type1_file = relationship_type_store.item_at_index(rel_type1.index)
        self.assertEquals(rel_type1, rel_type1_file)

        new_rel_type2_file = \
            relationship_type_store.item_at_index(new_rel_type2.index)
        self.assertEquals(new_rel_type2, new_rel_type2_file)

        rel_type3_file = relationship_type_store.item_at_index(rel_type3.index)
        self.assertEquals(rel_type3, rel_type3_file)

    def test_delete_relationship_type(self):
        """
        Tests that deleting 2 nodes in a database with 3 nodes works
        """
        relationship_type_store = RelationshipTypeStore()

        # Create 3 nodes
        rel_type1 = RelationshipType(1, True, 1)
        rel_type2 = RelationshipType(2, True, 2)
        rel_type3 = RelationshipType(3, True, 3)

        # Write them to the nodestore
        relationship_type_store.write_item(rel_type1)
        relationship_type_store.write_item(rel_type2)
        relationship_type_store.write_item(rel_type3)

        # Verify that they are in the store as expected
        rel_type1_file = relationship_type_store.item_at_index(rel_type1.index)
        self.assertEquals(rel_type1, rel_type1_file)

        rel_type2_file = relationship_type_store.item_at_index(rel_type2.index)
        self.assertEquals(rel_type2, rel_type2_file)

        rel_type3_file = relationship_type_store.item_at_index(rel_type3.index)
        self.assertEquals(rel_type3, rel_type3_file)

        # Delete nodes 1 and 3
        relationship_type_store.delete_item(rel_type1)
        relationship_type_store.delete_item(rel_type3)

        # Verify deleted node is deleted
        deleted_rel_type1_file = \
            relationship_type_store.item_at_index(rel_type1.index)
        self.assertEquals(deleted_rel_type1_file, None)

        # Verify unaffected node is as expected
        rel_type2_file = relationship_type_store.item_at_index(rel_type2.index)
        self.assertEquals(rel_type2, rel_type2_file)

        # Verify deleted node is deleted
        deleted_rel_type3_file = \
            relationship_type_store.item_at_index(rel_type3.index)
        self.assertEquals(deleted_rel_type3_file, None)