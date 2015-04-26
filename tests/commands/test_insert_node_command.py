import unittest

from graphene.commands import InsertNodeCommand
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.server.server import GrapheneServer

class TestInsertNodeCommand(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        self.server = GrapheneServer()
        self.sm = self.server.storage_manager

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_insert_single_node(self):
        assert self.server.doCommands("CREATE TYPE T ( a: int, b: string );", False)

    def test_init(self):
        cmd = InsertNodeCommand("foo")
        assert cmd.node_prop_list == "foo"

    def test_get_tt_of_string(self):
        empty_cmd = InsertNodeCommand(None)
        assert empty_cmd.get_type_type_of_string('"a"') == Property.PropertyType.string
        assert empty_cmd.get_type_type_of_string('true') == Property.PropertyType.bool
        assert empty_cmd.get_type_type_of_string('false') == Property.PropertyType.bool
        assert empty_cmd.get_type_type_of_string('34') == Property.PropertyType.int
        assert empty_cmd.get_type_type_of_string('3.4') == Property.PropertyType.undefined
        assert empty_cmd.get_type_type_of_string('-34') == Property.PropertyType.int

    def test_convert_to_value(self):
        empty_cmd = InsertNodeCommand(None)
        assert empty_cmd.convert_to_value('"a"', Property.PropertyType.string) == "a"
        assert empty_cmd.convert_to_value('true', Property.PropertyType.bool) == True
        assert empty_cmd.convert_to_value('false', Property.PropertyType.bool) == False
        assert empty_cmd.convert_to_value('34', Property.PropertyType.int) == 34
        assert empty_cmd.convert_to_value('-34', Property.PropertyType.int) == -34
