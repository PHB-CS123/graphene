import unittest

from graphene.storage.graphenestore import *
from graphene.storage.nodestore import *

class TestNodeStoreMethods(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True

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
        with self.assertRaises(ValueError):
            nodestore.write_node(empty_node)

    def test_write_read_1_node(self):
        """
        Tests that the Node written to the NodeStore is the Node that is read
        """
        # Create a node and add it to the NodeStore file
        nodestore = NodeStore()
        valid_node = Node(1, False, 1, 1)
        nodestore.write_node(valid_node)

        # Read the node from the NodeStore file
        valid_node_file = nodestore.node_at_index(valid_node.index)

        # Assert that the values are the same
        self.assertEquals(valid_node, valid_node_file)

    def test_write_read_2_nodes(self):
        """
        Tests that the 2 nodes written to the NodeStore are the 2 nodes read
        """

        # Create 2 nodes and add them to the NodeStore file
        nodestore = NodeStore()
        valid_node1 = Node(2, False, 2, 2)
        valid_node2 = Node(3, False, 3, 3)
        nodestore.write_node(valid_node1)
        nodestore.write_node(valid_node2)

        # Read the nodes from the NodeStore file
        valid_node1_file = nodestore.node_at_index(valid_node1.index)
        valid_node2_file = nodestore.node_at_index(valid_node2.index)

        # Make sure their values are the same
        self.assertEquals(valid_node1, valid_node1_file)
        self.assertEquals(valid_node2, valid_node2_file)

    def test_overwrite_node(self):
        """
        Tests that overwriting a node works
        """

        # Create a node that overwrites an existing node
        nodestore = NodeStore()
        # Get old node values and new node values
        old_node1 = Node(1, False, 1, 1)
        new_node2 = Node(2, True, 8, 8)
        old_node3 = Node(3, False, 3, 3)

        # Write the new node
        nodestore.write_node(new_node2)

        # Verify that the data is as expected
        old_node1_file = nodestore.node_at_index(old_node1.index)
        self.assertEquals(old_node1, old_node1_file)

        new_node2_file = nodestore.node_at_index(new_node2.index)
        self.assertEquals(new_node2, new_node2_file)

        old_node3_file = nodestore.node_at_index(old_node3.index)
        self.assertEquals(old_node3, old_node3_file)





