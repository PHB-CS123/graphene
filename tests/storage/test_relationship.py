import unittest

from graphene.storage.relationship import *


class TestRelationshipMethods(unittest.TestCase):
    def test_empty_init(self):
        """
        Tests that initializing a relationship with no arguments, uses the
        default values below.
        """
        # Create empty relationship
        relationship = Relationship()

        # Check values
        self.assertEquals(relationship.index, 0)
        self.assertEquals(relationship.inUse, True)
        self.assertEquals(relationship.direction, Relationship.Direction.right)
        self.assertEquals(relationship.firstNodeId, 0)
        self.assertEquals(relationship.secondNodeId, 0)
        self.assertEquals(relationship.relType, 0)
        self.assertEquals(relationship.firstPrevRelId, 0)
        self.assertEquals(relationship.firstNextRelId, 0)
        self.assertEquals(relationship.secondPrevRelId, 0)
        self.assertEquals(relationship.secondNextRelId, 0)
        self.assertEquals(relationship.propId, 0)

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
        relationship = Relationship(index, in_use, direction, first_node_id,
                                    second_node_id, rel_type, first_prev_rel_id,
                                    first_next_rel_id, second_prev_rel_id,
                                    second_next_rel_id, prop_id)

        # Check values
        self.assertEquals(relationship.index, 1)
        self.assertEquals(relationship.inUse, False)
        self.assertEquals(relationship.direction, Relationship.Direction.left)
        self.assertEquals(relationship.firstNodeId, 2)
        self.assertEquals(relationship.secondNodeId, 3)
        self.assertEquals(relationship.relType, 4)
        self.assertEquals(relationship.firstPrevRelId, 5)
        self.assertEquals(relationship.firstNextRelId, 6)
        self.assertEquals(relationship.secondPrevRelId, 7)
        self.assertEquals(relationship.secondNextRelId, 8)
        self.assertEquals(relationship.propId, 9)

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

        self.assertEquals(relationship1 == relationship2, True)
        self.assertEquals(relationship1 == relationship3, False)