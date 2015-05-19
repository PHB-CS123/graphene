import unittest

from graphene.commands import InsertNodeCommand
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.server.server import GrapheneServer
from graphene.utils.conversion import TypeConversion

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
