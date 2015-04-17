import unittest

from graphene.storage.node_store import *


class TestNodeStoreMethods(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_empty_init(self):
        """
        Test that initializing an empty NodeStore succeeds (file is opened)
        """
        try:
            NodeStore()
        except IOError:
            self.fail("NodeStore initializer failed: db file failed to open.")

    def test_double_init(self):
        """
        Test that initializing an empty NodeStore succeeds when
        repeated; i.e. the old file is reopened and no errors occur.
        """
        try:
            NodeStore()
        except IOError:
            self.fail("NodeStore initializer failed: "
                      "db file failed to open.")
        try:
            NodeStore()
        except IOError:
            self.fail("NodeStore initializer failed on second attempt: "
                      "db file failed to open.")

    def test_invalid_write(self):
        """
        Test that writing a node to index 0 raises an error
        """
        node_store = NodeStore()

        empty_node = Node()
        with self.assertRaises(ValueError):
            node_store.write_item(empty_node)

    def test_invalid_read(self):
        """
        Test that reading a node from index 0 raises an error
        """
        node_store = NodeStore()

        with self.assertRaises(ValueError):
            node_store.item_at_index(0)

    def test_write_read_1_node(self):
        """
        Tests that the node written to the NodeStore is the node that is read.
        """
        node_store = NodeStore()

        # Create a node and add it to the NodeStore
        node = Node(1, False, 1, 1, 1)
        node_store.write_item(node)

        # Read the node from the NodeStore file
        node_file = node_store.item_at_index(node.index)

        # Assert that the values are the same
        self.assertEquals(node, node_file)

    def test_write_read_2_nodes(self):
        """
        Tests when 2 nodes are written after 1 node to the NodeStore
        """
        node_store = NodeStore()

        # Create one node and write it to the NodeStore
        node1 = Node(1, False, 1, 1, 1)
        node_store.write_item(node1)

        # Create 2 nodes and add them to the NodeStore
        node2 = Node(2, False, 2, 2, 2)
        node3 = Node(3, False, 3, 3, 3)
        node_store.write_item(node2)
        node_store.write_item(node3)

        # Read the nodes from the NodeStore file
        node1_file = node_store.item_at_index(node1.index)
        node2_file = node_store.item_at_index(node2.index)
        node3_file = node_store.item_at_index(node3.index)

        # Make sure their values are the same
        self.assertEquals(node1, node1_file)
        self.assertEquals(node2, node2_file)
        self.assertEquals(node3, node3_file)

    def test_overwrite_node(self):
        """
        Tests that overwriting a node in a database with 3 nodes works
        """
        node_store = NodeStore()

        # Create 3 nodes
        node1 = Node(1, False, 1, 1, 1)
        node2 = Node(2, False, 2, 2, 2)
        node3 = Node(3, False, 3, 3, 3)

        # Write them to the nodestore
        node_store.write_item(node1)
        node_store.write_item(node2)
        node_store.write_item(node3)

        # Verify that they are in the store as expected
        node1_file = node_store.item_at_index(node1.index)
        self.assertEquals(node1, node1_file)

        node2_file = node_store.item_at_index(node2.index)
        self.assertEquals(node2, node2_file)

        node3_file = node_store.item_at_index(node3.index)
        self.assertEquals(node3, node3_file)

        # Create a new node2 and overwrite the old node2
        new_node2 = Node(2, True, 8, 8, 8)
        node_store.write_item(new_node2)

        # Verify that the data is still as expected
        node1_file = node_store.item_at_index(node1.index)
        self.assertEquals(node1, node1_file)

        new_node2_file = node_store.item_at_index(new_node2.index)
        self.assertEquals(new_node2, new_node2_file)

        node3_file = node_store.item_at_index(node3.index)
        self.assertEquals(node3, node3_file)

    def test_delete_node(self):
        """
        Tests that deleting 2 nodes in a database with 3 nodes works
        """
        node_store = NodeStore()

        # Create 3 nodes
        node1 = Node(1, True, 1, 1, 1)
        node2 = Node(2, True, 2, 2, 2)
        node3 = Node(3, True, 3, 3, 3)

        # Write them to the nodestore
        node_store.write_item(node1)
        node_store.write_item(node2)
        node_store.write_item(node3)

        # Verify that they are in the store as expected
        node1_file = node_store.item_at_index(node1.index)
        self.assertEquals(node1, node1_file)

        node2_file = node_store.item_at_index(node2.index)
        self.assertEquals(node2, node2_file)

        node3_file = node_store.item_at_index(node3.index)
        self.assertEquals(node3, node3_file)

        # Delete nodes 1 and 3
        node_store.delete_item(node1)
        node_store.delete_item(node3)

        # Create nodes 1 and 3 with zeroed out values
        zero_node1 = Node(node1.index, False, 0, 0, 0)
        zero_node3 = Node(node3.index, False, 0, 0, 0)

        # Verify deleted node is zeroed out
        deleted_node1_file = node_store.item_at_index(node1.index)
        self.assertEquals(zero_node1, deleted_node1_file)

        # Verify unaffected node is as expected
        node2_file = node_store.item_at_index(node2.index)
        self.assertEquals(node2, node2_file)

        # Verify deleted node is zeroed out
        deleted_node3_file = node_store.item_at_index(node3.index)
        self.assertEquals(zero_node3, deleted_node3_file)
