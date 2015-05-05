import unittest

from graphene.server.server import GrapheneServer
from graphene.query.planner import QueryPlanner
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.expressions import *
from graphene.errors import *
from graphene.traversal import Query

class TestQueryPlanner(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        self.server = GrapheneServer()
        self.sm = self.server.storage_manager

        self.server.doCommands("CREATE TYPE T ( a: int );", False)
        self.server.doCommands("INSERT NODE T(1), T(2), T(3), T(4), T(5);", False)

        self.server.doCommands("CREATE RELATION R ( b: int );", False)
        self.server.doCommands("INSERT RELATION T(a=1)-[R(2)]->T(a=2);")
        self.server.doCommands("INSERT RELATION T(a=1)-[R(3)]->T(a=3);")
        self.server.doCommands("INSERT RELATION T(a=2)-[R(6)]->T(a=3);")
        self.server.doCommands("INSERT RELATION T(a=3)-[R(12)]->T(a=4);")
        self.server.doCommands("INSERT RELATION T(a=3)-[R(15)]->T(a=5);")

        self.planner = QueryPlanner(self.sm)

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

    def test_get_schema(self):
        #ni = no ident
        n1, n1ni = MatchNode("t", "T"), MatchNode(None, "T")
        n2, n2ni = MatchNode("t2", "T"), MatchNode(None, "T")
        r, rni = MatchRelation("r", "R"), MatchRelation(None, "R")

        # (T)
        self.assertListEqual(self.planner.get_schema((n1ni,)),
            [('a', Property.PropertyType.int)])

        # (t:T)
        self.assertListEqual(self.planner.get_schema((n1,)),
            [('t.a', Property.PropertyType.int)])

        # (T)-[r:R]->(T) => no error, because duplicates will be stripped anyway
        self.assertListEqual(self.planner.get_schema((n1ni, r, n2ni), True),
            [('a', Property.PropertyType.int), ('r.b', Property.PropertyType.int),
            ('a', Property.PropertyType.int)])

        # (T)-[R]->(T) => error (duplicate), if the set is the full schema
        with self.assertRaises(DuplicatePropertyException):
            self.planner.get_schema((n1ni, rni, n2ni), True)

        # (T)-[R]->(T) => no error, if the set is not the full set (subset, so
        # anything not identified will be stripped later)
        self.assertListEqual(self.planner.get_schema((n1ni, rni, n2ni), False),
            [('a', Property.PropertyType.int), ('b', Property.PropertyType.int),
            ('a', Property.PropertyType.int)])

        # (t:T)-[R]->(t:T) => error (duplicate), same identifier
        with self.assertRaises(DuplicatePropertyException):
            self.planner.get_schema((n1, r, n1))

    def test_check_query_single_node(self):
        nc = (MatchNode("t", "T"),)

        # With identifier
        qc = (('t', 'a', '=', '1'),)
        try:
            self.planner.check_query(self.planner.get_schema(nc), nc, qc)
        except Exception:
            self.fail("check_query raised an Exception unexpectedly.")

        # Without identifier
        qc = ((None, 'a', '=', '1'),)
        try:
            self.planner.check_query(self.planner.get_schema(nc), nc, qc)
        except Exception:
            self.fail("check_query raised an Exception unexpectedly.")

        # No such property
        qc = ((None, 'b', '=', '1'),)
        with self.assertRaises(NonexistentPropertyException):
            self.planner.check_query(self.planner.get_schema(nc), nc, qc)

        # No such identifier
        qc = (('s', 'a', '=', '1'),)
        with self.assertRaises(NonexistentPropertyException):
            self.planner.check_query(self.planner.get_schema(nc), nc, qc)

    def test_check_query_relations(self):
        nc = (MatchNode("t", "T"), MatchRelation("r", "R"), MatchNode("t2", "T"))

        # With identifier
        qc = (('t', 'a', '=', '1'),)
        try:
            self.planner.check_query(self.planner.get_schema(nc), nc, qc)
        except Exception:
            self.fail("check_query raised an Exception unexpectedly.")

        qc = (('r', 'b', '=', '1'),)
        try:
            self.planner.check_query(self.planner.get_schema(nc), nc, qc)
        except Exception:
            self.fail("check_query raised an Exception unexpectedly.")

        # Without identifier, ambiguous
        qc = ((None, 'a', '=', '1'),)
        with self.assertRaises(AmbiguousPropertyException):
            self.planner.check_query(self.planner.get_schema(nc), nc, qc)

        # Without identifier, unambiguous
        qc = ((None, 'b', '=', '1'),)
        try:
            self.planner.check_query(self.planner.get_schema(nc), nc, qc)
        except Exception:
            self.fail("check_query raised an Exception unexpectedly.")

        # No such identifier
        qc = (('s', 'a', '=', '1'),)
        with self.assertRaises(NonexistentPropertyException):
            self.planner.check_query(self.planner.get_schema(nc), nc, qc)

    def test_reduce_query_chain(self):
        #ni = no ident
        n1, n1ni = MatchNode("t", "T"), MatchNode(None, "T")
        n2, n2ni = MatchNode("t2", "T"), MatchNode(None, "T")
        r, rni = MatchRelation("r", "R"), MatchRelation(None, "R")

        qc = (('t', 'a', '=', '1'), ('r', 'b', '>', '0'))
        expected = Query.parse_chain(self.sm, (('t', 'a', '=', '1'),), self.planner.get_schema((n1,)))
        result = self.planner.reduce_query_chain(qc, self.planner.get_schema((n1, r, n2ni)), 't')
        self.assertListEqual(result, expected)

        expected = Query.parse_chain(self.sm, (('r', 'b', '>', '0'),), self.planner.get_schema((r,)))
        result = self.planner.reduce_query_chain(qc, self.planner.get_schema((n1, r, n2ni)), 'r')
        self.assertListEqual(result, expected)

        expected = []
        result = self.planner.reduce_query_chain(qc, self.planner.get_schema((n1, r, n2ni)))
        self.assertListEqual(result, expected)

        qc = ((None, 'a', '=', '1'), (None, 'b', '>', '0'))
        expected = Query.parse_chain(self.sm, ((None, 'b', '>', '0'),), self.planner.get_schema((r,)))
        result = self.planner.reduce_query_chain(qc, self.planner.get_schema((r,)))
        self.assertListEqual(result, expected)

        # Note that this does not handle ambiguous names... check_query does
        qc = ((None, 'a', '=', '1'), (None, 'b', '>', '0'))
        expected = Query.parse_chain(self.sm, ((None, 'a', '=', '1'), (None, 'b', '>', '0')), self.planner.get_schema((n1, r, n2)))
        result = self.planner.reduce_query_chain(qc, self.planner.get_schema((n1, r, n2)))
        self.assertListEqual(result, expected)

        # Does handle nonexistent properties though!
        qc = ((None, 'c', '=', '1'),)
        with self.assertRaises(NonexistentPropertyException):
            self.planner.reduce_query_chain(qc, self.planner.get_schema((n1, r, n2)), throw=True)

        # Check error suppression
        qc = ((None, 'c', '=', '1'),)
        try:
            self.planner.reduce_query_chain(qc, self.planner.get_schema((n1, r, n2)), throw=False)
        except Exception:
            self.fail("reduce_query_chain threw error despite suppression being on")

    def test_execute_only_nodes(self):
        # Without identifier
        exp_schema = ['a']
        exp_vals = [(1,), (2,), (3,), (4,), (5,)]
        schema, results = self.planner.execute((MatchNode(None, "T"),), (), ())
        self.assertListEqual(schema, exp_schema)
        self.assertTrue(self.lists_equal_unordered(results, exp_vals))

        # With identifier
        exp_schema = ['t.a']
        exp_vals = [(1,), (2,), (3,), (4,), (5,)]
        schema, results = self.planner.execute((MatchNode("t", "T"),), (), ())
        self.assertListEqual(schema, exp_schema)
        self.assertTrue(self.lists_equal_unordered(results, exp_vals))

    def test_execute_one_relation(self):
        #ni = no ident
        n1, n1ni = MatchNode("t", "T"), MatchNode(None, "T")
        n2, n2ni = MatchNode("t2", "T"), MatchNode(None, "T")
        r, rni = MatchRelation("r", "R"), MatchRelation(None, "R")

        # (t:T)-[r:R]->(t2:T)
        exp_schema = ['t.a', 'r.b', 't2.a']
        exp_vals = [(1,2,2), (1,3,3), (2,6,3), (3,12,4), (3,15,5)]
        schema, results = self.planner.execute((n1, r, n2), (), ())
        self.assertListEqual(schema, exp_schema)
        self.assertTrue(self.lists_equal_unordered(results, exp_vals))

        # (t:T)-[R]->(t2:T)
        exp_schema = ['t.a', 't2.a']
        exp_vals = [(1,2), (1,3), (2,3), (3,4), (3,5)]
        schema, results = self.planner.execute((n1, rni, n2), (), ())
        self.assertListEqual(schema, exp_schema)
        self.assertTrue(self.lists_equal_unordered(results, exp_vals))

        # (t:T)-[R]->(T)
        exp_schema = ['t.a']
        exp_vals = [(1,), (1,), (2,), (3,), (3,)]
        schema, results = self.planner.execute((n1, rni, n2ni), (), ())
        self.assertListEqual(schema, exp_schema)
        self.assertTrue(self.lists_equal_unordered(results, exp_vals))

        # (T)-[R]->(t2:T)
        exp_schema = ['t2.a']
        exp_vals = [(2,), (3,), (3,), (4,), (5,)]
        schema, results = self.planner.execute((n1ni, rni, n2), (), ())
        self.assertListEqual(schema, exp_schema)
        self.assertTrue(self.lists_equal_unordered(results, exp_vals))

        # (T)-[r:R]->(T)
        exp_schema = ['r.b']
        exp_vals = [(2,), (3,), (6,), (12,), (15,)]
        schema, results = self.planner.execute((n1ni, r, n2ni), (), ())
        self.assertListEqual(schema, exp_schema)
        self.assertTrue(self.lists_equal_unordered(results, exp_vals))

        # (t:T)-[r:R]->(T)
        exp_schema = ['t.a', 'r.b']
        exp_vals = [(1,2), (1,3), (2,6), (3,12), (3,15)]
        schema, results = self.planner.execute((n1, r, n2ni), (), ())
        self.assertListEqual(schema, exp_schema)
        self.assertTrue(self.lists_equal_unordered(results, exp_vals))

    def test_execute_multi_relation(self):
        assert True

    def test_execute_with_query(self):
        assert True

    def test_execute_with_return(self):
        assert True

    def test_execute_with_ambiguous_names(self):
        assert True

    def test_execute_with_duplicate_names(self):
        assert True
