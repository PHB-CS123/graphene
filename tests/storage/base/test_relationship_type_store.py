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
        self.assertEquals(no_item, GeneralStore.EOF)

    def test_write_read_1_relationship_type(self):
        """
        Tests that the relationship type written to the RelationshipTypeStore
        is the relationship type that is read.
        """
        relationship_type_store = RelationshipTypeStore()

        # Create a relationship type and add it to the RelationshipTypeStore
        rel_type = RelationshipType(1, False, 1)
        relationship_type_store.write_item(rel_type)

        # Read the relationship type from the RelationshipTypeStore file
        rel_type_file = relationship_type_store.item_at_index(rel_type.index)

        # Assert that the values are the same
        self.assertEquals(rel_type, rel_type_file)

    def test_write_read_2_relationship_types(self):
        """
        Tests when 2 relationship types are written after 1 relationship type
        to the RelationshipTypeStore
        """
        relationship_type_store = RelationshipTypeStore()

        # Create one relationship type and write it to the RelationshipTypeStore
        rel_type1 = RelationshipType(1, False, 1)
        relationship_type_store.write_item(rel_type1)

        # Create 2 relationship types and add them to the RelationshipTypeStore
        rel_type2 = RelationshipType(2, False, 2)
        rel_type3 = RelationshipType(3, False, 3)
        relationship_type_store.write_item(rel_type2)
        relationship_type_store.write_item(rel_type3)

        # Read the relationship types from the RelationshipTypeStore file
        rel_type1_file = relationship_type_store.item_at_index(rel_type1.index)
        rel_type2_file = relationship_type_store.item_at_index(rel_type2.index)
        rel_type3_file = relationship_type_store.item_at_index(rel_type3.index)

        # Make sure their values are the same
        self.assertEquals(rel_type1, rel_type1_file)
        self.assertEquals(rel_type2, rel_type2_file)
        self.assertEquals(rel_type3, rel_type3_file)

    def test_overwrite_relationship_type(self):
        """
        Tests that overwriting a relationship type in a database with 3
        relationship types works
        """
        relationship_type_store = RelationshipTypeStore()

        # Create 3 relationship types
        rel_type1 = RelationshipType(1, False, 1)
        rel_type2 = RelationshipType(2, False, 2)
        rel_type3 = RelationshipType(3, False, 3)

        # Write them to the RelationshipTypeStore
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
        Tests that deleting 2 relationship types in a database with 3
        relationship types works
        """
        relationship_type_store = RelationshipTypeStore()

        # Create 3 relationship types
        rel_type1 = RelationshipType(1, True, 1)
        rel_type2 = RelationshipType(2, True, 2)
        rel_type3 = RelationshipType(3, True, 3)

        # Write them to the RelationshipTypeStore
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

        # Delete relationship types 1 and 3
        relationship_type_store.delete_item(rel_type1)
        # Deleting from end of file, should return EOF when read
        relationship_type_store.delete_item(rel_type3)

        # Verify deleted relationship types are deleted
        deleted_rel_type1_file = \
            relationship_type_store.item_at_index(rel_type1.index)
        self.assertEquals(deleted_rel_type1_file, None)
        deleted_rel_type3_file = \
            relationship_type_store.item_at_index(rel_type3.index)
        self.assertEquals(deleted_rel_type3_file, EOF)

        # Verify unaffected relationship type is as expected
        rel_type2_file = relationship_type_store.item_at_index(rel_type2.index)
        self.assertEquals(rel_type2, rel_type2_file)
