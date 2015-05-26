import unittest
import os

from graphene.commands import MatchCommand
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.server.server import GrapheneServer
from graphene.utils.pretty_printer import PrettyPrinter

class TestMatchCommand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        GrapheneStore.TESTING = True
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        cls.server = GrapheneServer()
        cls.sm = cls.server.storage_manager
        cls.server.doCommands("CREATE TYPE T ( a: int );", False)
        cls.server.doCommands("INSERT NODE T(1), T(2), T(3), T(4), T(5);", False)

        cls.devnull = open(os.devnull, "w")

    @classmethod
    def tearDownClass(cls):
        """
        Clean the database so that the tests are independent of one another
        """
        del cls.sm
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def assertListEqualUnsorted(self, given, expected):
        self.assertListEqual(sorted(given), sorted(expected))

    def test_match_all(self):
        cmd = self.server.parseString("MATCH (t:T);")[0]

        exp_vals = [
            [1],
            [2],
            [3],
            [4],
            [5],
        ]

        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertListEqualUnsorted(ret_vals, exp_vals)

    def test_match_where(self):
        cmd = self.server.parseString("MATCH (t:T) WHERE a = 1;")[0]

        exp_vals = [
            [1],
        ]

        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertListEqualUnsorted(ret_vals, exp_vals)

        cmd = self.server.parseString("MATCH (t:T) WHERE a > 2;")[0]

        exp_vals = [
            [3],
            [4],
            [5],
        ]

        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertListEqualUnsorted(ret_vals, exp_vals)

        cmd = self.server.parseString("MATCH (t:T) WHERE a != 2;")[0]

        exp_vals = [
            [1],
            [3],
            [4],
            [5],
        ]

        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertListEqualUnsorted(ret_vals, exp_vals)

        cmd = self.server.parseString("MATCH (t:T) WHERE a > 6;")[0]

        exp_vals = []

        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertListEqualUnsorted(ret_vals, exp_vals)

    def test_match_where_and(self):
        cmd = self.server.parseString("MATCH (t:T) WHERE a > 1 AND a < 5;")[0]

        exp_vals = [
            [2],
            [3],
            [4],
        ]

        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertListEqualUnsorted(ret_vals, exp_vals)

    def test_match_where_badname(self):
        # No identifier, property name doesn't exist
        cmd = self.server.parseString("MATCH (t:T) WHERE b = 1;")[0]
        with self.assertRaises(Exception):
            cmd.execute(self.sm, self.devnull)
        # Correct identifier, property name still doesn't exist
        cmd = self.server.parseString("MATCH (t:T) WHERE t.b = 1;")[0]
        with self.assertRaises(Exception):
            cmd.execute(self.sm, self.devnull)
        # Incorrect identifier despite correct property name
        cmd = self.server.parseString("MATCH (t:T) WHERE t2.a = 1;")[0]
        with self.assertRaises(Exception):
            cmd.execute(self.sm, self.devnull)
