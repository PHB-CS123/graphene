import unittest

from graphene.storage.nodestore import *

class TestNodeStoreMethods(unittest.TestCase):
    def test_empty_init(self):
        """
        Test that initializing an empty NodeStore succeeds (file is opened)
        """
        try:
            NodeStore()
        except IOError:
            self.fail("NodeStore initializer failed: db file failed to open.")

    def test_invalid_write(self):
        """
        Test that writing a node to offset 0 raises an error
        """
        nodestore = NodeStore()
        empty_node = Node()
        self.assertRaises(ValueError, nodestore.write_node(empty_node))

    def test_write_read(self):
        """
        Tests that the Node written to the NodeStore is the Node that is read
        """
        nodestore = NodeStore()
        valid_node = Node(1, 0, 1, 1)
        nodestore.write_node(valid_node)
        self.assertEquals(nodestore.node_at_index(valid_node.index),
                          valid_node)