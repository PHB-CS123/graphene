import unittest
import os

from graphene.commands import MatchCommand
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.server.server import GrapheneServer
from graphene.utils.pretty_printer import PrettyPrinter

class TestMatchCommand(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        self.server = GrapheneServer()
        self.sm = self.server.storage_manager
        self.server.doCommands("CREATE TYPE T ( a: int );", False)
        self.server.doCommands("INSERT NODE T(1), T(2), T(3), T(4), T(5);", False)

        self.devnull = open(os.devnull, "w")

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def lists_equal_unordered(self, values, expected):
        tvalues = map(tuple, values)
        for tv in tvalues:
            try:
                idx = expected.index(tv)
            except ValueError:
                # not in list!
                return False
            del expected[idx]
        if len(expected) > 0:
            # didn't hit everything in expected list
            return False
        return True

    def test_match_all(self):
        cmd = self.server.parseString("MATCH (t:T);")[0]

        exp_vals = [
            (1,),
            (2,),
            (3,),
            (4,),
            (5,),
        ]

        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertTrue(self.lists_equal_unordered(ret_vals, exp_vals))

    def test_match_where(self):
        cmd = self.server.parseString("MATCH (t:T) WHERE a = 1;")[0]

        exp_vals = [
            (1,),
        ]

        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertTrue(self.lists_equal_unordered(ret_vals, exp_vals))

        cmd = self.server.parseString("MATCH (t:T) WHERE a > 2;")[0]

        exp_vals = [
            (3,),
            (4,),
            (5,),
        ]

        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertTrue(self.lists_equal_unordered(ret_vals, exp_vals))

        cmd = self.server.parseString("MATCH (t:T) WHERE a != 2;")[0]

        exp_vals = [
            (1,),
            (3,),
            (4,),
            (5,),
        ]

        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertTrue(self.lists_equal_unordered(ret_vals, exp_vals))

        cmd = self.server.parseString("MATCH (t:T) WHERE a > 6;")[0]

        exp_vals = []

        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertTrue(self.lists_equal_unordered(ret_vals, exp_vals))

    def test_match_where_and(self):
        cmd = self.server.parseString("MATCH (t:T) WHERE a > 1 AND a < 5;")[0]

        exp_vals = [
            (2,),
            (3,),
            (4,),
        ]

        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertTrue(self.lists_equal_unordered(ret_vals, exp_vals))

    def test_match_where_badname(self):
        cmd = self.server.parseString("MATCH (t:T) WHERE b = 1;")[0]
        with self.assertRaises(Exception):
            cmd.execute(self.sm, self.devnull)
