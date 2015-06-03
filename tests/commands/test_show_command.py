import unittest

from graphene.commands import ShowCommand
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.utils import PrettyPrinter
from graphene.server.server import GrapheneServer
import StringIO

class TestShowCommand(unittest.TestCase):
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
        del self.sm
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_no_type(self):
        # Create command and ensure that it has the right type
        cmd = ShowCommand(ShowCommand.ShowType.TYPES)
        self.assertEquals(cmd.show_type, ShowCommand.ShowType.TYPES)

        # Create dummy output stream for testing
        out = StringIO.StringIO()
        cmd.execute(self.sm, output=out)
        self.assertEquals(out.getvalue(), "No types found.\n")
        out.close()

    def test_one_type(self):
        # Pretty print expected output for testing later
        exp_stream = StringIO.StringIO()
        PrettyPrinter.print_table(["T"], ["TYPES"], exp_stream)
        expected = exp_stream.getvalue()
        exp_stream.close()

        t = self.sm.create_node_type("T", (("a", "int"), ("b", "string")))
        cmd = ShowCommand(ShowCommand.ShowType.TYPES)
        self.assertEquals(cmd.show_type, ShowCommand.ShowType.TYPES)
        # Dummy output stream
        out = StringIO.StringIO()
        cmd.execute(self.sm, output=out)
        self.assertEquals(out.getvalue(), expected)
        out.close()

    def test_no_relations(self):
        # Create command and ensure that it has the right type
        cmd = ShowCommand(ShowCommand.ShowType.RELATIONS)
        self.assertEquals(cmd.show_type, ShowCommand.ShowType.RELATIONS)

        # Create dummy output stream for testing
        out = StringIO.StringIO()
        cmd.execute(self.sm, output=out)
        self.assertEquals(out.getvalue(), "No relations found.\n")
        out.close()

    def test_one_relation(self):
        # Pretty print expected output for testing later
        exp_stream = StringIO.StringIO()
        PrettyPrinter.print_table(["R"], ["RELATIONS"], exp_stream)
        expected = exp_stream.getvalue()
        exp_stream.close()

        t = self.sm.create_relationship_type("R", (("a", "int"), ("b", "string")))
        cmd = ShowCommand(ShowCommand.ShowType.RELATIONS)
        self.assertEquals(cmd.show_type, ShowCommand.ShowType.RELATIONS)
        # Dummy output stream
        out = StringIO.StringIO()
        cmd.execute(self.sm, output=out)
        self.assertEquals(out.getvalue(), expected)
        out.close()
