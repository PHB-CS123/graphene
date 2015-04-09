import unittest

from graphene.storage.node import *

class TestNodeMethods(unittest.TestCase):
    def test_empty_init(self):
        node = Node()
        self.assertEquals(node.index, 0)
        self.assertEquals(node.inUse, False)
        self.assertEquals(node.relId, 0)
        self.assertEquals(node.propId, 0)

    def test_init(self):
        node = Node(32, True, 42, 21)
        self.assertEquals(node.index, 32)
        self.assertEquals(node.inUse, True)
        self.assertEquals(node.relId, 42)
        self.assertEquals(node.propId, 21)

    def test_eq(self):
        node1 = Node(24, True, 31, 21)
        node2 = Node(24, True, 31, 21)
        node3 = Node(24, False, 31, 21)

        self.assertEquals(node1 == node2, True)
        self.assertEquals(node1 == node3, False)
