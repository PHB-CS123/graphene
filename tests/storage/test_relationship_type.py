import unittest

from graphene.storage.relationship_type import *


class TestRelationshipTypeMethods(unittest.TestCase):
    def test_empty_init(self):
        """
        Tests that initializing a relationship type with no arguments, uses the
        default values below.
        """
        # Create empty relationship type
        relType = RelationshipType()

        # Check values
        self.assertEquals(relType.index, 0)
        self.assertEquals(relType.inUse, True)
        self.assertEquals(relType.typeBlockId, 0)

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
        relType = RelationshipType(index, in_use, type_block_id)

        # Check values
        self.assertEquals(relType.index, 1)
        self.assertEquals(relType.inUse, False)
        self.assertEquals(relType.typeBlockId, 42)

    def test_eq(self):
        """
        Tests that == operator returns True when two relationship types are
        equal and False when they are not
        """
        relationshipType1 = RelationshipType(1, False, 42)
        relationshipType2 = RelationshipType(1, False, 42)
        relationshipType3 = RelationshipType(20, True, 21)

        self.assertTrue(relationshipType1 == relationshipType2)
        self.assertFalse(relationshipType1 == relationshipType3)
        self.assertFalse(relationshipType2 == relationshipType3)
        self.assertFalse(relationshipType1 == 1)
