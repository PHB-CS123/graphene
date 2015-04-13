import unittest

from graphene.storage.node import *


class TestNodeMethods(unittest.TestCase):
    def test_empty_init(self):
        """
        Tests that initializing a Node with no arguments, uses the
        default values below.
        """
        node = Node()
        self.assertEquals(node.index, 0)
        self.assertEquals(node.inUse, True)
        self.assertEquals(node.relId, 0)
        self.assertEquals(node.propId, 0)

    def test_init(self):
        """
        Tests that initializing a Node with a set of values stores
        those values properly
        """
        node = Node(32, False, 42, 21)
        self.assertEquals(node.index, 32)
        self.assertEquals(node.inUse, False)
        self.assertEquals(node.relId, 42)
        self.assertEquals(node.propId, 21)

    def test_eq(self):
        """
        Tests that == operator returns True when two nodes are equal
        and False when they are not
        """
        node1 = Node(24, True, 31, 21)
        node2 = Node(24, True, 31, 21)
        node3 = Node(24, False, 31, 21)

        self.assertTrue(node1 == node2)
        self.assertFalse(node1 == node3)
        self.assertFalse(node2 == node3)
        self.assertFalse(node1 == 1)
