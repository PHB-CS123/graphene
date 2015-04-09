import unittest

from graphene.storage.node import *

class TestNodeMethods(unittest.TestCase):
    def test_empty_init(self):
        node = Node()
        self.assertEquals(node.index, 0)
        self.assertEquals(node.inUse, 0)
        self.assertEquals(node.relId, 0)
        self.assertEquals(node.propId, 0)

    def test_init(self):
        node = Node(32, 1, 42, 21)
        self.assertEquals(node.index, 32)
        self.assertEquals(node.inUse, 1)
        self.assertEquals(node.relId, 42)
        self.assertEquals(node.propId, 21)
