import unittest

from graphene.storage.base.relationship_type import *


class TestRelationshipTypeMethods(unittest.TestCase):
    def test_empty_init(self):
        """
        Tests that initializing a relationship type with no arguments, uses the
        default values below.
        """
        # Create empty relationship type
        rel_type = RelationshipType()

        # Check values
        self.assertEquals(rel_type.index, 0)
        self.assertEquals(rel_type.inUse, True)
        self.assertEquals(rel_type.typeBlockId, 0)

    def test_init(self):
        """
        Tests that initializing a relationship type with a set of values stores
        those values properly
        """
        # Relationship type values
        index = 1
        in_use = False
        type_block_id = 42

        # Create relationship type
        rel_type = RelationshipType(index, in_use, type_block_id)

        # Check values
        self.assertEquals(rel_type.index, 1)
        self.assertEquals(rel_type.inUse, False)
        self.assertEquals(rel_type.typeBlockId, 42)

    def test_eq(self):
        """
        Tests that == operator returns True when two relationship types are
        equal and False when they are not
        """
        relationship_type1 = RelationshipType(1, False, 42)
        relationship_type2 = RelationshipType(1, False, 42)
        relationship_type3 = RelationshipType(20, True, 21)

        self.assertTrue(relationship_type1 == relationship_type2)
        self.assertFalse(relationship_type1 == relationship_type3)
        self.assertFalse(relationship_type2 == relationship_type3)
        self.assertFalse(relationship_type1 == 1)
