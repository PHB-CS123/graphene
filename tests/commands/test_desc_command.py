import unittest
import StringIO

from graphene.commands import DescCommand
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.utils import PrettyPrinter
from graphene.server.server import GrapheneServer

class TestShowCommand(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True
        # Set to no colors to avoid escape sequences in output
        PrettyPrinter.TESTING = True

        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        self.server = GrapheneServer()
        self.sm = self.server.storage_manager

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        self.sm.close()

    def test_no_type(self):
        # Create command and ensure that it has the right type
        cmd = DescCommand("Foo", DescCommand.DescType.TYPE)
        self.assertEquals(cmd.type_name, "Foo")

        # Create dummy output stream for testing
        out = StringIO.StringIO()
        cmd.execute(self.sm, output=out)
        self.assertEquals(out.getvalue(), "Type Foo does not exist.\n")
        out.close()

    def test_one_type(self):
        printer = PrettyPrinter()
        # Pretty print expected output for testing later
        exp_stream = StringIO.StringIO()
        printer.print_table((("a", "int"), ("b", "string")), ["NAME", "TYPE"], exp_stream)
        expected = exp_stream.getvalue()
        exp_stream.close()

        t = self.sm.create_node_type("T", (("a", "int"), ("b", "string")))
        cmd = DescCommand("T", DescCommand.DescType.TYPE)
        self.assertEquals(cmd.type_name, "T")
        # Dummy output stream
        out = StringIO.StringIO()
        cmd.execute(self.sm, output=out)
        self.assertEquals(out.getvalue(), expected)
        out.close()

    def test_no_relation(self):
        # Create command and ensure that it has the right type
        cmd = DescCommand("Foo", DescCommand.DescType.RELATION)
        self.assertEquals(cmd.type_name, "Foo")

        # Create dummy output stream for testing
        out = StringIO.StringIO()
        cmd.execute(self.sm, output=out)
        self.assertEquals(out.getvalue(), "Type Foo does not exist.\n")
        out.close()

    def test_one_type(self):
        printer = PrettyPrinter()
        # Pretty print expected output for testing later
        exp_stream = StringIO.StringIO()
        printer.print_table((("a", "int"), ("b", "string")), ["NAME", "TYPE"], exp_stream)
        expected = exp_stream.getvalue()
        exp_stream.close()

        t = self.sm.create_relationship_type("R", (("a", "int"), ("b", "string")))
        cmd = DescCommand("R", DescCommand.DescType.RELATION)
        self.assertEquals(cmd.type_name, "R")
        # Dummy output stream
        out = StringIO.StringIO()
        cmd.execute(self.sm, output=out)
        self.assertEquals(out.getvalue(), expected)
        out.close()
