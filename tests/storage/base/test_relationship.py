import unittest

from graphene.storage.base.relationship import *


class TestRelationshipMethods(unittest.TestCase):
    def test_empty_init(self):
        """
        Tests that initializing a relationship with no arguments, uses the
        default values below.
        """
        # Create empty relationship
        rel = Relationship()

        # Check values
        self.assertEquals(rel.index, 0)
        self.assertEquals(rel.inUse, True)
        self.assertEquals(rel.direction, Relationship.Direction.undefined)
        self.assertEquals(rel.firstNodeId, 0)
        self.assertEquals(rel.secondNodeId, 0)
        self.assertEquals(rel.relType, 0)
        self.assertEquals(rel.firstPrevRelId, 0)
        self.assertEquals(rel.firstNextRelId, 0)
        self.assertEquals(rel.secondPrevRelId, 0)
        self.assertEquals(rel.secondNextRelId, 0)
        self.assertEquals(rel.propId, 0)

    def test_init(self):
        """
        Tests that initializing a relationship with a set of values stores
        those values properly
        """
        # Relationship values
        index = 1
        in_use = False
        direction = Relationship.Direction.left
        first_node_id = 2
        second_node_id = 3
        rel_type = 4
        first_prev_rel_id = 5
        first_next_rel_id = 6
        second_prev_rel_id = 7
        second_next_rel_id = 8
        prop_id = 9

        # Create relationship
        rel = Relationship(index, in_use, direction, first_node_id,
                           second_node_id, rel_type, first_prev_rel_id,
                           first_next_rel_id, second_prev_rel_id,
                           second_next_rel_id, prop_id)

        # Check values
        self.assertEquals(rel.index, 1)
        self.assertEquals(rel.inUse, False)
        self.assertEquals(rel.direction, Relationship.Direction.left)
        self.assertEquals(rel.firstNodeId, 2)
        self.assertEquals(rel.secondNodeId, 3)
        self.assertEquals(rel.relType, 4)
        self.assertEquals(rel.firstPrevRelId, 5)
        self.assertEquals(rel.firstNextRelId, 6)
        self.assertEquals(rel.secondPrevRelId, 7)
        self.assertEquals(rel.secondNextRelId, 8)
        self.assertEquals(rel.propId, 9)

    def test_eq(self):
        """
        Tests that == operator returns True when two relationships are equal
        and False when they are not
        """
        relationship1 = Relationship(1, True, Relationship.Direction.left,
                                     2, 3, 4, 5, 6, 7, 8, 9)
        relationship2 = Relationship(1, True, Relationship.Direction.left,
                                     2, 3, 4, 5, 6, 7, 8, 9)
        relationship3 = Relationship(9, False, Relationship.Direction.right,
                                     8, 7, 6, 5, 4, 3, 2, 1)

        self.assertTrue(relationship1 == relationship2)
        self.assertFalse(relationship1 == relationship3)
        self.assertFalse(relationship2 == relationship3)
        self.assertFalse(relationship1 == 1)
