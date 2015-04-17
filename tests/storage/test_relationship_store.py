import unittest

from graphene.storage.relationship_store import *


class TestRelationshipStoreMethods(unittest.TestCase):
    def setUp(self):
        """
        Set up the GrapheneStore so that it writes datafiles to the testing
        directory
        """
        GrapheneStore.TESTING = True

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_empty_init(self):
        """
        Test that initializing an empty RelationshipStore succeeds
        (file is opened successfully)
        """
        try:
            RelationshipStore()
        except IOError:
            self.fail("RelationshipStore initializer failed: "
                      "db file failed to open.")

    def test_double_init(self):
        """
        Test that initializing an empty RelationshipStore succeeds when
        repeated; i.e. the old file is reopened and no errors occur.
        """
        try:
            RelationshipStore()
        except IOError:
            self.fail("RelationshipStore initializer failed: "
                      "db file failed to open.")
        try:
            RelationshipStore()
        except IOError:
            self.fail("RelationshipStore initializer failed on second attempt: "
                      "db file failed to open.")

    def test_invalid_write(self):
        """
        Test that writing a relationship to offset 0 raises an error
        """
        relationship_store = RelationshipStore()

        empty_relationship = Relationship()
        with self.assertRaises(ValueError):
            relationship_store.write_item(empty_relationship)

        bad_direction = Relationship(1, False, "bad_dir",
                                    2, 3, 4, 5, 6, 7, 8, 9)
        with self.assertRaises(TypeError):
            relationship_store.write_item(bad_direction)

    def test_invalid_read(self):
        """
        Test that reading a relationship from index 0 raises an error
        """
        relationship_store = RelationshipStore()

        with self.assertRaises(ValueError):
            relationship_store.item_at_index(0)

    def test_write_read_1_relationship(self):
        """
        Tests that the relationship written to the RelationshipStore is the
        relationship that is read.
        """
        relationship_store = RelationshipStore()

        # Create a relationship and add it to the RelationshipStore file
        relationship = Relationship(1, False, Relationship.Direction.left,
                                    2, 3, 4, 5, 6, 7, 8, 9)
        relationship_store.write_item(relationship)

        # Read the relationship from the RelationshipStore file
        relationship_file = \
            relationship_store.item_at_index(relationship.index)

        # Assert that the values are the same
        self.assertEquals(relationship, relationship_file)

    def test_write_read_2_relationships(self):
        """
        Tests when 2 relationships are written after 1 relationship
        to the RelationshipStore
        """
        relationship_store = RelationshipStore()

        # Create one relationship and write it to the RelationshipStore
        relationship1 = Relationship(1, False, Relationship.Direction.left,
                                     2, 3, 4, 5, 6, 7, 8, 9)
        relationship_store.write_item(relationship1)

        # Create 2 relationships and add them to the RelationshipStore
        relationship2 = Relationship(2, False, Relationship.Direction.right,
                                     4, 6, 8, 10, 12, 14, 16, 18)
        relationship3 = Relationship(9, False, Relationship.Direction.right,
                                     8, 7, 6, 5, 4, 3, 2, 1)
        relationship_store.write_item(relationship2)
        relationship_store.write_item(relationship3)

        # Read the relationships from the RelationshipStore file
        relationship1_file = \
            relationship_store.item_at_index(relationship1.index)
        relationship2_file = \
            relationship_store.item_at_index(relationship2.index)
        relationship3_file = \
            relationship_store.item_at_index(relationship3.index)

        # Make sure their values are the same
        self.assertEquals(relationship1, relationship1_file)
        self.assertEquals(relationship2, relationship2_file)
        self.assertEquals(relationship3, relationship3_file)

    def test_overwrite_relationship(self):
        """
        Tests that overwriting a relationship in a database with 3
        relationships works
        """
        relationship_store = RelationshipStore()

        # Create 3 relationships
        relationship1 = Relationship(1, False, Relationship.Direction.left,
                                     2, 3, 4, 5, 6, 7, 8, 9)
        relationship2 = Relationship(2, False, Relationship.Direction.right,
                                     4, 6, 8, 10, 12, 14, 16, 18)
        relationship3 = Relationship(9, False, Relationship.Direction.right,
                                     8, 7, 6, 5, 4, 3, 2, 1)

        # Write them to the relationship_store
        relationship_store.write_item(relationship1)
        relationship_store.write_item(relationship2)
        relationship_store.write_item(relationship3)

        # Verify that they are in the store as expected
        relationship1_file = \
            relationship_store.item_at_index(relationship1.index)
        self.assertEquals(relationship1, relationship1_file)

        relationship2_file = \
            relationship_store.item_at_index(relationship2.index)
        self.assertEquals(relationship2, relationship2_file)

        relationship3_file = \
            relationship_store.item_at_index(relationship3.index)
        self.assertEquals(relationship3, relationship3_file)

        # Create a new relationship2 and overwrite the old relationship2
        new_relationship2 = Relationship(3, True, Relationship.Direction.left,
                                         6, 9, 12, 15, 18, 21, 24, 27)
        relationship_store.write_item(new_relationship2)

        # Verify that the data is still as expected
        relationship1_file = \
            relationship_store.item_at_index(relationship1.index)
        self.assertEquals(relationship1, relationship1_file)

        new_relationship2_file = \
            relationship_store.item_at_index(new_relationship2.index)
        self.assertEquals(new_relationship2, new_relationship2_file)

        relationship3_file = \
            relationship_store.item_at_index(relationship3.index)
        self.assertEquals(relationship3, relationship3_file)

    def test_delete_relationship(self):
        """
        Tests that deleting 2 relationships in a database with 3
        relationships works
        """
        relationship_store = RelationshipStore()

        # Create 3 relationships
        rel1 = Relationship(1, True, Relationship.Direction.left,
                            2, 3, 4, 5, 6, 7, 8, 9)
        rel2 = Relationship(2, True, Relationship.Direction.right,
                            4, 6, 8, 10, 12, 14, 16, 18)
        rel3 = Relationship(9, True, Relationship.Direction.right,
                            8, 7, 6, 5, 4, 3, 2, 1)

        # Write them to the relationship_store
        relationship_store.write_item(rel1)
        relationship_store.write_item(rel2)
        relationship_store.write_item(rel3)

        # Verify that they are in the store as expected
        rel1_file = relationship_store.item_at_index(rel1.index)
        self.assertEquals(rel1, rel1_file)

        rel2_file = relationship_store.item_at_index(rel2.index)
        self.assertEquals(rel2, rel2_file)

        rel3_file = relationship_store.item_at_index(rel3.index)
        self.assertEquals(rel3, rel3_file)

        # Delete relationships 1 and 3
        relationship_store.delete_item(rel1)
        relationship_store.delete_item(rel3)

        # Create relationships 1 and 3 with zeroed out values
        zero_rel1 = Relationship(rel1.index, False,
                                 Relationship.Direction.undefined,
                                 0, 0, 0, 0, 0, 0, 0, 0)
        zero_rel3 = Relationship(rel3.index, False,
                                 Relationship.Direction.undefined,
                                 0, 0, 0, 0, 0, 0, 0, 0)

        # Verify deleted relationship is zeroed out
        del_rel1_file = relationship_store.item_at_index(rel1.index)
        self.assertEquals(zero_rel1, del_rel1_file)

        # Verify unaffected relationship is as expected
        rel2_file = relationship_store.item_at_index(rel2.index)
        self.assertEquals(rel2, rel2_file)

        # Verify deleted relationship is zeroed out
        del_rel3_file = relationship_store.item_at_index(rel3.index)
        self.assertEquals(zero_rel3, del_rel3_file)
