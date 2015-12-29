import unittest

from graphene.commands import UpdateNodeCommand
from graphene.errors import NonexistentPropertyException, TypeMismatchException
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.server.server import GrapheneServer
from graphene.utils.conversion import TypeConversion
from graphene.utils.pretty_printer import PrettyPrinter

class TestUpdateNodeCommand(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True
        # Set to no colors to avoid escape sequences in output
        PrettyPrinter.NO_COLORS = True

        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        self.server = GrapheneServer()
        self.sm = self.server.storage_manager

        self.node_type = self.sm.create_node_type("T", (("a", "int"), ("b", "string"), ("c", "int[]")))

        self.n1, p1 = self.sm.insert_node(self.node_type, ((Property.PropertyType.int, 1), (Property.PropertyType.string, "foo"), (Property.PropertyType.intArray, [0])))
        self.n2, p2 = self.sm.insert_node(self.node_type, ((Property.PropertyType.int, 2), (Property.PropertyType.string, "bar"), (Property.PropertyType.intArray, [1])))
        self.n3, p3 = self.sm.insert_node(self.node_type, ((Property.PropertyType.int, 3), (Property.PropertyType.string, "baz"), (Property.PropertyType.intArray, [0, 1])))

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        self.sm.close()

    def test_init(self):
        query_chain = [((None, 'a'), '=', '1')]
        update_dict = {"a": '4', "b": '"foo"'}
        cmd = UpdateNodeCommand("T", query_chain, update_dict)
        self.assertEqual(cmd.node_type, "T")
        self.assertListEqual(cmd.qc, query_chain)
        self.assertDictEqual(cmd.update, update_dict)

    def test_update_with_query(self):
        query_chain = [((None, 'a'), '=', '1')]
        update_dict = {"a": '4', "b": '"boo"', "c": '[]'}
        cmd = UpdateNodeCommand("T", query_chain, update_dict)

        self.assertListEqual(self.sm.get_node(self.n1.index).properties, [1, 'foo', [0]])
        self.assertListEqual(self.sm.get_node(self.n2.index).properties, [2, 'bar', [1]])
        self.assertListEqual(self.sm.get_node(self.n3.index).properties, [3, 'baz', [0, 1]])

        cmd.execute(self.sm)

        self.assertListEqual(self.sm.get_node(self.n1.index).properties, [4, 'boo', []])
        self.assertListEqual(self.sm.get_node(self.n2.index).properties, [2, 'bar', [1]])
        self.assertListEqual(self.sm.get_node(self.n3.index).properties, [3, 'baz', [0, 1]])

    def test_update_without_query(self):
        update_dict = {"a": '4', "b": '"boo"', "c": '[]'}
        cmd = UpdateNodeCommand("T", None, update_dict)

        self.assertListEqual(self.sm.get_node(self.n1.index).properties, [1, 'foo', [0]])
        self.assertListEqual(self.sm.get_node(self.n2.index).properties, [2, 'bar', [1]])
        self.assertListEqual(self.sm.get_node(self.n3.index).properties, [3, 'baz', [0, 1]])

        cmd.execute(self.sm)

        self.assertListEqual(self.sm.get_node(self.n1.index).properties, [4, 'boo', []])
        self.assertListEqual(self.sm.get_node(self.n2.index).properties, [4, 'boo', []])
        self.assertListEqual(self.sm.get_node(self.n3.index).properties, [4, 'boo', []])

    def test_nonexistent_property(self):
        update_dict = {"qux": '"boo"'}
        cmd = UpdateNodeCommand("T", None, update_dict)

        with self.assertRaises(NonexistentPropertyException):
            cmd.execute(self.sm)

    def test_type_mismatch(self):
        update_dict = {"a": '"blah"'}
        cmd = UpdateNodeCommand("T", None, update_dict)

        with self.assertRaises(TypeMismatchException):
            cmd.execute(self.sm)

    def test_array_type_mismatch(self):
        update_dict = {"a": "[]"}
        cmd = UpdateNodeCommand("T", None, update_dict)

        with self.assertRaises(TypeMismatchException):
            cmd.execute(self.sm)
