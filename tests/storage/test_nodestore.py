import unittest

from graphene.storage.graphenestore import *
from graphene.storage.nodestore import *

class TestNodeStoreMethods(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphenestore = GrapheneStore()
        graphenestore.remove_test_datafiles()

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
        Tests that the Node written to the NodeStore is the Node that is read.
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
        Tests when 2 nodes are written after 1 node to the NodeStore
        """

        nodestore = NodeStore()

        # Create one node and write it to the NodeStore
        node1 = Node(1, False, 1, 1)
        nodestore.write_node(node1)

        # Create 2 nodes and add them to the NodeStore file
        node2 = Node(2, False, 2, 2)
        node3 = Node(3, False, 3, 3)
        nodestore.write_node(node2)
        nodestore.write_node(node3)

        # Read the nodes from the NodeStore file
        node1_file = nodestore.node_at_index(node1.index)
        node2_file = nodestore.node_at_index(node2.index)
        node3_file = nodestore.node_at_index(node3.index)

        # Make sure their values are the same
        self.assertEquals(node1, node1_file)
        self.assertEquals(node2, node2_file)
        self.assertEquals(node3, node3_file)

    def test_overwrite_node(self):
        """
        Tests that overwriting a node in a database with 2 nodes works
        """


        nodestore = NodeStore()

        # Create 3 old nodes
        old_node1 = Node(1, False, 1, 1)
        old_node2 = Node(2, False, 2, 2)
        old_node3 = Node(3, False, 3, 3)

        # Write them to the nodestore
        nodestore.write_node(old_node1)
        nodestore.write_node(old_node2)
        nodestore.write_node(old_node3)

        # Verify that they are in the store as expected
        old_node1_file = nodestore.node_at_index(old_node1.index)
        self.assertEquals(old_node1, old_node1_file)

        old_node2_file = nodestore.node_at_index(old_node2.index)
        self.assertEquals(old_node2, old_node2_file)

        old_node3_file = nodestore.node_at_index(old_node3.index)
        self.assertEquals(old_node3, old_node3_file)

        # Create a new node2 abd overwrite the old node2
        new_node2 = Node(2, True, 8, 8)
        nodestore.write_node(new_node2)

        # Verify that the data is still as expected
        old_node1_file = nodestore.node_at_index(old_node1.index)
        self.assertEquals(old_node1, old_node1_file)

        new_node2_file = nodestore.node_at_index(new_node2.index)
        self.assertEquals(new_node2, new_node2_file)

        old_node3_file = nodestore.node_at_index(old_node3.index)
        self.assertEquals(old_node3, old_node3_file)

