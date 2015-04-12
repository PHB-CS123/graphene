import unittest

from graphene.storage.relationshipstore import *


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
        graphenestore = GrapheneStore()
        graphenestore.remove_test_datafiles()

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

    def test_invalid_write(self):
        """
        Test that writing a relationship to offset 0 raises an error
        """
        relationship_store = RelationshipStore()
        empty_relationship = Relationship()
        with self.assertRaises(ValueError):
            relationship_store.write_relationship(empty_relationship)

    def test_invalid_read(self):
        """
        Test that reading a relationship from index 0 raises an error
        """
        relationship_store = RelationshipStore()
        with self.assertRaises(ValueError):
            relationship_store.relationship_at_index(0)

    def test_write_read_1_relationship(self):
        """
        Tests that the relationship written to the RelationshipStore is the
        relationship that is read.
        """
        # Create a relationship and add it to the RelationshipStore file
        relationship_store = RelationshipStore()
        relationship = Relationship(1, False, Relationship.Direction.left,
                                    2, 3, 4, 5, 6, 7, 8, 9)
        relationship_store.write_relationship(relationship)

        # Read the relationship from the RelationshipStore file
        relationship_file = \
            relationship_store.relationship_at_index(relationship.index)

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
        relationship_store.write_relationship(relationship1)

        # Create 2 relationships and add them to the RelationshipStore
        relationship2 = Relationship(2, False, Relationship.Direction.right,
                                     4, 6, 8, 10, 12, 14, 16, 18)
        relationship3 = Relationship(9, False, Relationship.Direction.right,
                                     8, 7, 6, 5, 4, 3, 2, 1)
        relationship_store.write_relationship(relationship2)
        relationship_store.write_relationship(relationship3)

        # Read the relationships from the RelationshipStore file
        relationship1_file = \
            relationship_store.relationship_at_index(relationship1.index)
        relationship2_file = \
            relationship_store.relationship_at_index(relationship2.index)
        relationship3_file = \
            relationship_store.relationship_at_index(relationship3.index)

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
        relationship_store.write_relationship(relationship1)
        relationship_store.write_relationship(relationship2)
        relationship_store.write_relationship(relationship3)

        # Verify that they are in the store as expected
        relationship1_file = \
            relationship_store.relationship_at_index(relationship1.index)
        self.assertEquals(relationship1, relationship1_file)

        relationship2_file = \
            relationship_store.relationship_at_index(relationship2.index)
        self.assertEquals(relationship2, relationship2_file)

        relationship3_file = \
            relationship_store.relationship_at_index(relationship3.index)
        self.assertEquals(relationship3, relationship3_file)

        # Create a new relationship2 and overwrite the old relationship2
        new_relationship2 = Relationship(3, True, Relationship.Direction.left,
                                         6, 9, 12, 15, 18, 21, 24, 27)
        relationship_store.write_relationship(new_relationship2)

        # Verify that the data is still as expected
        relationship1_file = \
            relationship_store.relationship_at_index(relationship1.index)
        self.assertEquals(relationship1, relationship1_file)

        new_relationship2_file = \
            relationship_store.relationship_at_index(new_relationship2.index)
        self.assertEquals(new_relationship2, new_relationship2_file)

        relationship3_file = \
            relationship_store.relationship_at_index(relationship3.index)
        self.assertEquals(relationship3, relationship3_file)

