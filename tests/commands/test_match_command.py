import unittest
import os

from graphene.commands import MatchCommand
from graphene.errors import TooManyClausesException
from graphene.expressions import OptionalClause
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.server.server import GrapheneServer
from graphene.utils.pretty_printer import PrettyPrinter

class TestMatchCommand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        GrapheneStore.TESTING = True
        # Set to no colors to avoid escape sequences in output
        PrettyPrinter.TESTING = True

        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        cls.server = GrapheneServer()
        cls.sm = cls.server.storage_manager
        cls.server.doCommands("CREATE TYPE T ( a: int );", False)
        cls.server.doCommands("INSERT NODE T(1), T(2), T(3), T(4), T(5);", False)
        cls.server.doCommands("CREATE RELATION R ();", False)
        cls.server.doCommands("INSERT RELATION T(a=1)-[R]->T(a=2), "
                              "T(a=1)-[R]->T(a=3), T(a=1)-[R]->T(a=4), "
                              "T(a=1)-[R]->T(a=5), T(a=2)-[R]->T(a=3)", False)

        cls.devnull = open(os.devnull, "w")

    @classmethod
    def tearDownClass(cls):
        """
        Clean the database so that the tests are independent of one another
        """
        cls.sm.close()

    def assertListEqualUnsorted(self, given, expected):
        self.assertListEqual(sorted(given), sorted(expected))

    def test_parse_clauses(self):
        cmd = MatchCommand(None, None, None)

        with self.assertRaises(TooManyClausesException):
            cmd.parse_clauses(((OptionalClause.ORDERBY, None),(OptionalClause.ORDERBY, None),))

        with self.assertRaises(TooManyClausesException):
            cmd.parse_clauses(((OptionalClause.RETURN, None),(OptionalClause.RETURN, None),))

        with self.assertRaises(TooManyClausesException):
            cmd.parse_clauses(((OptionalClause.LIMIT, None),(OptionalClause.LIMIT, None),))

        rc, limit, orderby = cmd.parse_clauses([])
        self.assertTupleEqual(rc, ())
        self.assertEqual(limit, 0)
        self.assertListEqual(orderby, [])

        rc, limit, orderby = cmd.parse_clauses([(OptionalClause.LIMIT, 5),
            (OptionalClause.RETURN, (1, 2)), (OptionalClause.ORDERBY, [3, 4])])
        self.assertTupleEqual(rc, (1, 2))
        self.assertEqual(limit, 5)
        self.assertListEqual(orderby, [3, 4])

        rc, limit, orderby = cmd.parse_clauses([(OptionalClause.LIMIT, -5)])
        self.assertTupleEqual(rc, ())
        self.assertEqual(limit, 0)
        self.assertListEqual(orderby, [])

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

    def test_limit_node(self):
        # WARNING: Limits just take the elements in the order they were added
        # to the database!! There is no real meaning to the order that you get.

        # Limit of zero means just everything
        cmd = self.server.parseString("MATCH (t:T) LIMIT 0")[0]

        exp_vals = [ [1], [2], [3], [4], [5] ]
        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertListEqualUnsorted(ret_vals, exp_vals)

        # Limit less than number of rows
        cmd = self.server.parseString("MATCH (t:T) LIMIT 2")[0]

        exp_vals = [ [1], [2] ]
        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertListEqualUnsorted(ret_vals, exp_vals)

        # Limit more than number of rows (same as zero)
        cmd = self.server.parseString("MATCH (t:T) LIMIT 30")[0]

        exp_vals = [ [1], [2], [3], [4], [5] ]
        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertListEqualUnsorted(ret_vals, exp_vals)

    def test_limit_rel(self):
        # WARNING: Limits just take the elements in the order they were added
        # to the database!! There is no real meaning to the order that you get.
        #
        # Limit of zero means just everything
        cmd = self.server.parseString("MATCH (t:T)-[R]->(t2:T) LIMIT 0")[0]

        exp_vals = [ [1, 2], [1, 3], [1, 4], [1, 5], [2, 3] ]
        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertListEqualUnsorted(ret_vals, exp_vals)

        # Limit less than number of rows
        cmd = self.server.parseString("MATCH (t:T)-[R]->(t2:T) LIMIT 2")[0]

        exp_vals = [ [1, 2], [1, 3] ]
        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertListEqualUnsorted(ret_vals, exp_vals)

        # Limit more than number of rows (same as zero)
        cmd = self.server.parseString("MATCH (t:T)-[R]->(t2:T) LIMIT 30")[0]

        exp_vals = [ [1, 2], [1, 3], [1, 4], [1, 5], [2, 3] ]
        ret_vals = cmd.execute(self.sm, self.devnull)
        self.assertListEqualUnsorted(ret_vals, exp_vals)
