import unittest

from graphene.commands import DescTypeCommand
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
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_no_type(self):
        # Create command and ensure that it has the right type
        cmd = DescTypeCommand("Foo")
        self.assertEquals(cmd.type_name, "Foo")

        # Create dummy output stream for testing
        out = StringIO.StringIO()
        cmd.execute(self.sm, output=out)
        self.assertEquals(out.getvalue(), "Type Foo does not exist.")
        out.close()

    def test_one_type(self):
        # Pretty print expected output for testing later
        exp_stream = StringIO.StringIO()
        PrettyPrinter.print_table((("a", "int"), ("b", "string")), ["NAME", "TYPE"], exp_stream)
        expected = exp_stream.getvalue()
        exp_stream.close()

        t = self.sm.create_node_type("T", (("a", "int"), ("b", "string")))
        cmd = DescTypeCommand("T")
        self.assertEquals(cmd.type_name, "T")
        # Dummy output stream
        out = StringIO.StringIO()
        cmd.execute(self.sm, output=out)
        self.assertEquals(out.getvalue(), expected)
        out.close()
