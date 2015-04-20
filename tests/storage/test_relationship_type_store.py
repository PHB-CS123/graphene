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
        Test that initializing an empty RelationshipTypeStore succeeds (file is opened)
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

    def test_write_read_1_relationship_type(self):
        """
        Tests that the node written to the NodeStore is the node that is read.
        """
        relationship_type_store = RelationshipTypeStore()

        # Create a node and add it to the NodeStore
        relType = RelationshipType(1, False, 1)
        relationship_type_store.write_item(relType)

        # Read the node from the NodeStore file
        relType_file = relationship_type_store.item_at_index(relType.index)

        # Assert that the values are the same
        self.assertEquals(relType, relType_file)

    def test_write_read_2_relationship_types(self):
        """
        Tests when 2 nodes are written after 1 node to the NodeStore
        """
        relationship_type_store = RelationshipTypeStore()

        # Create one node and write it to the NodeStore
        relType1 = RelationshipType(1, False, 1)
        relationship_type_store.write_item(relType1)

        # Create 2 nodes and add them to the NodeStore
        relType2 = RelationshipType(2, False, 2)
        relType3 = RelationshipType(3, False, 3)
        relationship_type_store.write_item(relType2)
        relationship_type_store.write_item(relType3)

        # Read the nodes from the NodeStore file
        relType1_file = relationship_type_store.item_at_index(relType1.index)
        relType2_file = relationship_type_store.item_at_index(relType2.index)
        relType3_file = relationship_type_store.item_at_index(relType3.index)

        # Make sure their values are the same
        self.assertEquals(relType1, relType1_file)
        self.assertEquals(relType2, relType2_file)
        self.assertEquals(relType3, relType3_file)

    def test_overwrite_relationship_type(self):
        """
        Tests that overwriting a node in a database with 3 nodes works
        """
        relationship_type_store = RelationshipTypeStore()

        # Create 3 nodes
        relType1 = RelationshipType(1, False, 1)
        relType2 = RelationshipType(2, False, 2)
        relType3 = RelationshipType(3, False, 3)

        # Write them to the nodestore
        relationship_type_store.write_item(relType1)
        relationship_type_store.write_item(relType2)
        relationship_type_store.write_item(relType3)

        # Verify that they are in the store as expected
        relType1_file = relationship_type_store.item_at_index(relType1.index)
        self.assertEquals(relType1, relType1_file)

        relType2_file = relationship_type_store.item_at_index(relType2.index)
        self.assertEquals(relType2, relType2_file)

        relType3_file = relationship_type_store.item_at_index(relType3.index)
        self.assertEquals(relType3, relType3_file)

        # Create a new relType2 and overwrite the old relType2
        new_relType2 = RelationshipType(2, True, 8)
        relationship_type_store.write_item(new_relType2)

        # Verify that the data is still as expected
        relType1_file = relationship_type_store.item_at_index(relType1.index)
        self.assertEquals(relType1, relType1_file)

        new_relType2_file = relationship_type_store.item_at_index(new_relType2.index)
        self.assertEquals(new_relType2, new_relType2_file)

        relType3_file = relationship_type_store.item_at_index(relType3.index)
        self.assertEquals(relType3, relType3_file)

    def test_delete_relationship_type(self):
        """
        Tests that deleting 2 nodes in a database with 3 nodes works
        """
        relationship_type_store = RelationshipTypeStore()

        # Create 3 nodes
        relType1 = RelationshipType(1, True, 1)
        relType2 = RelationshipType(2, True, 2)
        relType3 = RelationshipType(3, True, 3)

        # Write them to the nodestore
        relationship_type_store.write_item(relType1)
        relationship_type_store.write_item(relType2)
        relationship_type_store.write_item(relType3)

        # Verify that they are in the store as expected
        relType1_file = relationship_type_store.item_at_index(relType1.index)
        self.assertEquals(relType1, relType1_file)

        relType2_file = relationship_type_store.item_at_index(relType2.index)
        self.assertEquals(relType2, relType2_file)

        relType3_file = relationship_type_store.item_at_index(relType3.index)
        self.assertEquals(relType3, relType3_file)

        # Delete nodes 1 and 3
        relationship_type_store.delete_item(relType1)
        relationship_type_store.delete_item(relType3)

        # Verify deleted node is deleted
        deleted_relType1_file = \
            relationship_type_store.item_at_index(relType1.index)
        self.assertEquals(deleted_relType1_file, None)

        # Verify unaffected node is as expected
        relType2_file = relationship_type_store.item_at_index(relType2.index)
        self.assertEquals(relType2, relType2_file)

        # Verify deleted node is deleted
        deleted_relType3_file = \
            relationship_type_store.item_at_index(relType3.index)
        self.assertEquals(deleted_relType3_file, None)