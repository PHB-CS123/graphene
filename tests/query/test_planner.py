import unittest

from graphene.server.server import GrapheneServer
from graphene.query.planner import QueryPlanner
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.expressions import *
from graphene.errors import *
from graphene.traversal import Query

class TestQueryPlanner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        GrapheneStore.TESTING = True
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        cls.server = GrapheneServer()
        cls.sm = cls.server.storage_manager

        cls.server.doCommands("CREATE TYPE T ( a: int );", False)
        cls.server.doCommands("INSERT NODE T(1), T(2), T(3), T(4), T(5);", False)
        cls.server.doCommands("CREATE TYPE S ( c: int );", False)
        cls.server.doCommands("INSERT NODE S(7);", False)

        cls.server.doCommands("CREATE RELATION R ( b: int );", False)
        cls.server.doCommands("INSERT RELATION T(a=1)-[R(2)]->T(a=2);")
        cls.server.doCommands("INSERT RELATION T(a=1)-[R(3)]->T(a=3);")
        cls.server.doCommands("INSERT RELATION T(a=2)-[R(6)]->T(a=3);")
        cls.server.doCommands("INSERT RELATION T(a=3)-[R(12)]->T(a=4);")
        cls.server.doCommands("INSERT RELATION T(a=3)-[R(15)]->T(a=5);")
        cls.server.doCommands("INSERT RELATION S(c=7)-[R(0)]->T(a=5);")

        cls.planner = QueryPlanner(cls.sm)

    @classmethod
    def tearDownClass(cls):
        """
        Clean the database so that the tests are independent of one another
        """
        cls.sm.close()

    def assertListEqualUnsorted(self, given, expected):
        self.assertListEqual(sorted(given), sorted(expected))

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
        schema = self.planner.get_schema(nc)

        # query_chain is None
        try:
            self.planner.check_query(schema, None)
        except Exception:
            self.fail("check_query raised an Exception unexpectedly.")

        # With identifier
        qc = ((('t', 'a'), '=', '1'),)
        try:
            self.planner.check_query(schema, qc)
        except Exception:
            self.fail("check_query raised an Exception unexpectedly.")

        # Without identifier
        qc = (((None, 'a'), '=', '1'),)
        try:
            self.planner.check_query(schema, qc)
        except Exception:
            self.fail("check_query raised an Exception unexpectedly.")

        # No such property
        qc = (((None, 'b'), '=', '1'),)
        with self.assertRaises(NonexistentPropertyException):
            self.planner.check_query(schema, qc)

        # No such identifier
        qc = ((('s', 'a'), '=', '1'),)
        with self.assertRaises(NonexistentPropertyException):
            self.planner.check_query(schema, qc)

    def test_check_query_relations(self):
        nc = (MatchNode("t", "T"), MatchRelation("r", "R"), MatchNode("t2", "T"))
        schema = self.planner.get_schema(nc)

        # With identifier
        qc = ((('t', 'a'), '=', '1'),)
        try:
            self.planner.check_query(schema, qc)
        except Exception:
            self.fail("check_query raised an Exception unexpectedly.")

        qc = ((('r', 'b'), '=', '1'),)
        try:
            self.planner.check_query(schema, qc)
        except Exception:
            self.fail("check_query raised an Exception unexpectedly.")

        # With two identifiers
        qc = ((('t', 'a'), '=', ('t2', 'a')),)
        try:
            self.planner.check_query(schema, qc)
        except Exception:
            self.fail("check_query raised an Exception unexpectedly.")

        # Without identifier, ambiguous
        qc = (((None, 'a'), '=', '1'),)
        with self.assertRaises(AmbiguousPropertyException):
            self.planner.check_query(schema, qc)

        qc = ((('r', 'b'), '=', (None, 'a')),)
        with self.assertRaises(AmbiguousPropertyException):
            self.planner.check_query(schema, qc)

        # Without identifier, unambiguous
        qc = (((None, 'b'), '=', '1'),)
        try:
            self.planner.check_query(schema, qc)
        except Exception:
            self.fail("check_query raised an Exception unexpectedly.")

        # No such identifier
        qc = ((('s', 'a'), '=', '1'),)
        with self.assertRaises(NonexistentPropertyException):
            self.planner.check_query(schema, qc)

        qc = ((('t', 'a'), '=', ('s', 'a')),)
        with self.assertRaises(NonexistentPropertyException):
            self.planner.check_query(schema, qc)

        qc = ((('t', 'a'), '=', (None, 'q')),)
        with self.assertRaises(NonexistentPropertyException):
            self.planner.check_query(schema, qc)

    def test_get_orderby_indexes(self):
        nc = (MatchNode("t", "T"), MatchRelation("r", "R"), MatchNode("t2", "T"))
        schema = self.planner.get_schema(nc)

        chain = [((None, 'a'), 'ASC')]
        with self.assertRaises(AmbiguousPropertyException):
            self.planner.get_orderby_indexes(schema, chain)

        chain = [((None, 'q'), 'ASC')]
        with self.assertRaises(NonexistentPropertyException):
            self.planner.get_orderby_indexes(schema, chain)

        chain = [(('r', 'a'), 'ASC')]
        with self.assertRaises(NonexistentPropertyException):
            self.planner.get_orderby_indexes(schema, chain)

        chain = [(('t', 'a'), 'ASC')]
        result = self.planner.get_orderby_indexes(schema, chain)
        self.assertListEqual(result, [(0, 1)])

        chain = [(('t', 'a'), None)]
        result = self.planner.get_orderby_indexes(schema, chain)
        self.assertListEqual(result, [(0, 1)])

        chain = [(('t', 'a'), 'DESC')]
        result = self.planner.get_orderby_indexes(schema, chain)
        self.assertListEqual(result, [(0, -1)])

        chain = [((None, 'b'), 'ASC')]
        result = self.planner.get_orderby_indexes(schema, chain)
        self.assertListEqual(result, [(1, 1)])

    def test_get_orderby_fn(self):
        nc = (MatchNode("t", "T"), MatchRelation("r", "R"), MatchNode("t2", "T"))
        schema_rel = self.planner.get_schema(nc)
        schema = self.planner.get_schema((MatchNode("t", "T"),))

        chain = [(('t', 'a'), 'ASC')]
        cmp_fn = self.planner.get_orderby_fn(schema, chain, is_relation=False)

        # Nodes are T[1], T[2], T[3], T[4], T[5]
        node1, node2 = self.sm.get_node(1), self.sm.get_node(2)
        self.assertListEqual(sorted([node1, node1], cmp=cmp_fn), [node1, node1])
        self.assertListEqual(sorted([node2, node1], cmp=cmp_fn), [node1, node2])

        chain = [(('t', 'a'), 'DESC')]
        cmp_fn = self.planner.get_orderby_fn(schema, chain, is_relation=False)
        self.assertListEqual(sorted([node1, node2], cmp=cmp_fn), [node2, node1])

        chain = [(('r', 'b'), 'ASC')]
        cmp_fn = self.planner.get_orderby_fn(schema_rel, chain, is_relation=True)

        self.assertListEqual(sorted([([1,2,3], None), ([3,1,2], None)], cmp=cmp_fn), [([3,1,2], None), ([1,2,3], None)])
        self.assertListEqual(sorted([([1,2,3], None), ([3,2,2], None)], cmp=cmp_fn), [([1,2,3], None), ([3,2,2], None)])

    def test_execute_only_nodes(self):
        # Without identifier
        exp_schema = ['a']
        exp_vals = [[1], [2], [3], [4], [5]]
        schema, results = self.planner.execute((MatchNode(None, "T"),), None, None)
        self.assertListEqual(schema, exp_schema)
        self.assertListEqual(results, exp_vals)

        # With identifier
        exp_schema = ['t.a']
        exp_vals = [[1], [2], [3], [4], [5]]
        schema, results = self.planner.execute((MatchNode("t", "T"),), None, None)
        self.assertListEqual(schema, exp_schema)
        self.assertListEqual(results, exp_vals)

    def test_execute_one_relation(self):
        #ni = no ident
        n1, n1ni = MatchNode("t", "T"), MatchNode(None, "T")
        n2, n2ni = MatchNode("t2", "T"), MatchNode(None, "T")
        r, rni = MatchRelation("r", "R"), MatchRelation(None, "R")

        # (t:T)-[r:R]->(t2:T)
        exp_schema = ['t.a', 'r.b', 't2.a']
        exp_vals = [[1,2,2], [1,3,3], [2,6,3], [3,12,4], [3,15,5]]
        schema, results = self.planner.execute((n1, r, n2), None, None)
        self.assertListEqual(schema, exp_schema)
        self.assertListEqual(results, exp_vals)

        # (t:T)-[R]->(t2:T)
        exp_schema = ['t.a', 't2.a']
        exp_vals = [[1,2], [1,3], [2,3], [3,4], [3,5]]
        schema, results = self.planner.execute((n1, rni, n2), None, None)
        self.assertListEqual(schema, exp_schema)
        self.assertListEqual(results, exp_vals)

        # (t:T)-[R]->(T)
        exp_schema = ['t.a']
        exp_vals = [[1], [1], [2], [3], [3]]
        schema, results = self.planner.execute((n1, rni, n2ni), None, None)
        self.assertListEqual(schema, exp_schema)
        self.assertListEqual(results, exp_vals)

        # (T)-[R]->(t2:T)
        exp_schema = ['t2.a']
        exp_vals = [[2], [3], [3], [4], [5]]
        schema, results = self.planner.execute((n1ni, rni, n2), None, None)
        self.assertListEqual(schema, exp_schema)
        self.assertListEqual(results, exp_vals)

        # (T)-[r:R]->(T)
        exp_schema = ['r.b']
        exp_vals = [[2], [3], [6], [12], [15]]
        schema, results = self.planner.execute((n1ni, r, n2ni), None, None)
        self.assertListEqual(schema, exp_schema)
        self.assertListEqual(results, exp_vals)

        # (t:T)-[r:R]->(T)
        exp_schema = ['t.a', 'r.b']
        exp_vals = [[1,2], [1,3], [2,6], [3,12], [3,15]]
        schema, results = self.planner.execute((n1, r, n2ni), None, None)
        self.assertListEqual(schema, exp_schema)
        self.assertListEqual(results, exp_vals)

    def test_execute_multi_relation(self):
        #ni = no ident
        n1, n1ni = MatchNode("t", "T"), MatchNode(None, "T")
        n2, n2ni = MatchNode("t2", "T"), MatchNode(None, "T")
        n3, n3ni = MatchNode("t3", "T"), MatchNode(None, "T")
        r, rni = MatchRelation("r", "R"), MatchRelation(None, "R")
        r2, r2ni = MatchRelation("r2", "R"), MatchRelation(None, "R")

        # (t:T)-[r:R]->(t2:T)-[r2:R]->(t3:T)
        exp_schema = ['t.a', 'r.b', 't2.a', 'r2.b', 't3.a']
        exp_vals = [[1,2,2,6,3], [1,3,3,12,4], [1,3,3,15,5], [2,6,3,12,4], [2,6,3,15,5]]
        schema, results = self.planner.execute((n1, r, n2, r2, n3), None, None)
        self.assertListEqual(schema, exp_schema)
        self.assertListEqualUnsorted(results, exp_vals)

        # (t:T)-[R]->(T)-[R]->(t3:T)
        exp_schema = ['t.a', 't3.a']
        exp_vals = [[1,3], [1,4], [1,5], [2,4], [2,5]]
        schema, results = self.planner.execute((n1, rni, n2ni, r2ni, n3), None, None)
        self.assertListEqual(schema, exp_schema)
        self.assertListEqualUnsorted(results, exp_vals)

    def test_execute_with_query(self):
        #ni = no ident
        n1, n1ni = MatchNode("t", "T"), MatchNode(None, "T")
        n2, n2ni = MatchNode("t2", "T"), MatchNode(None, "T")
        n3, n3ni = MatchNode("t3", "T"), MatchNode(None, "T")
        r, rni = MatchRelation("r", "R"), MatchRelation(None, "R")
        r2, r2ni = MatchRelation("r2", "R"), MatchRelation(None, "R")

        # (t:T)-[r:R]->(t2:T)-[r2:R]->(t3:T)
        exp_schema = ['t.a', 'r.b', 't2.a', 'r2.b', 't3.a']
        # node queries
        exp_vals = [[1,2,2,6,3], [1,3,3,12,4], [1,3,3,15,5]]
        schema, results = self.planner.execute((n1, r, n2, r2, n3), ((('t','a'),'=','1'),), None)
        self.assertListEqual(schema, exp_schema)
        self.assertListEqualUnsorted(results, exp_vals)

        exp_vals = [[1,3,3,12,4], [1,3,3,15,5], [2,6,3,12,4], [2,6,3,15,5]]
        schema, results = self.planner.execute((n1, r, n2, r2, n3), ((('t2','a'),'=','3'),), None)
        self.assertListEqualUnsorted(results, exp_vals)

        exp_vals = [[1,3,3,12,4], [2,6,3,12,4]]
        schema, results = self.planner.execute((n1, r, n2, r2, n3), ((('t3','a'),'=','4'),), None)
        self.assertListEqualUnsorted(results, exp_vals)

        # relation queries
        exp_vals = [[1,2,2,6,3]]
        schema, results = self.planner.execute((n1, r, n2, r2, n3), ((('r','b'),'=','2'),), None)
        self.assertListEqualUnsorted(results, exp_vals)

    def test_execute_with_return(self):
        #ni = no ident
        n1, n1ni = MatchNode("t", "T"), MatchNode(None, "T")
        n2, n2ni = MatchNode("t2", "T"), MatchNode(None, "T")
        n3, n3ni = MatchNode("t3", "T"), MatchNode(None, "T")
        r, rni = MatchRelation("r", "R"), MatchRelation(None, "R")
        r2, r2ni = MatchRelation("r2", "R"), MatchRelation(None, "R")

        # (t:T)-[r:R]->(t2:T)-[r2:R]->(t3:T) RETURN t.a
        exp_schema = ['t.a']
        # node queries
        exp_vals = [[1],[1],[1],[2],[2]]
        schema, results = self.planner.execute((n1, r, n2, r2, n3), None, (('t', 'a'),))
        self.assertListEqual(schema, exp_schema)
        self.assertListEqualUnsorted(results, exp_vals)

    def test_execute_with_ambiguous_names(self):
        #ni = no ident
        n1, n1ni = MatchNode("t", "T"), MatchNode(None, "T")
        n2, n2ni = MatchNode("t2", "T"), MatchNode(None, "T")
        n3, n3ni = MatchNode("t3", "T"), MatchNode(None, "T")
        r, rni = MatchRelation("r", "R"), MatchRelation(None, "R")
        r2, r2ni = MatchRelation("r2", "R"), MatchRelation(None, "R")

        # (t:T)-[r:R]->(t2:T)-[r2:R]->(t3:T) WHERE a = 1
        with self.assertRaises(AmbiguousPropertyException):
            self.planner.execute((n1, r, n2, r2, n3), (((None, 'a'), '=', '1'),), None)

        # (t:T)-[r:R]->(t2:T)-[r2:R]->(t3:T) RETURN a
        with self.assertRaises(AmbiguousPropertyException):
            self.planner.execute((n1, r, n2, r2, n3), None, ((None, 'a'),))

    def test_execute_with_duplicate_names(self):
        #ni = no ident
        n1, n1ni = MatchNode("t", "T"), MatchNode(None, "T")
        r, rni = MatchRelation("r", "R"), MatchRelation(None, "R")

        with self.assertRaises(DuplicatePropertyException):
            self.planner.execute((n1, r, n1), None, None)

    def test_execute_limit(self):
        #ni = no ident
        n1, n1ni = MatchNode("t", "T"), MatchNode(None, "T")
        n2, n2ni = MatchNode("t2", "T"), MatchNode(None, "T")
        r, rni = MatchRelation("r", "R"), MatchRelation(None, "R")

        exp_vals = [[1], [2], [3]]
        schema, results = self.planner.execute((n1ni,), None, None, limit=3)
        self.assertListEqual(results, exp_vals)

        exp_vals = [[1], [2], [3], [4], [5]]
        schema, results = self.planner.execute((n1ni,), None, None, limit=0)
        self.assertListEqual(results, exp_vals)
        schema, results = self.planner.execute((n1ni,), None, None, limit=6)
        self.assertListEqual(results, exp_vals)

        exp_vals = [[1,2,2], [1,3,3], [2,6,3]]
        schema, results = self.planner.execute((n1, r, n2), None, None, limit=3)
        self.assertListEqual(results, exp_vals)

    def test_execute_orderby(self):
        #ni = no ident
        n1, n1ni = MatchNode("t", "T"), MatchNode(None, "T")
        n2, n2ni = MatchNode("t2", "T"), MatchNode(None, "T")
        r, rni = MatchRelation("r", "R"), MatchRelation(None, "R")

        exp_vals = [[5], [4], [3], [2], [1]]
        schema, results = self.planner.execute((n1ni,), None, None, orderby=[((None, 'a'), 'DESC')])
        self.assertListEqual(results, exp_vals)

        exp_vals = [[3, 12, 4], [3, 15, 5], [2,6,3], [1,2,2], [1,3,3]]
        schema, results = self.planner.execute((n1, r, n2), None, None, orderby=[(('t', 'a'), 'DESC')])
        self.assertListEqual(results, exp_vals)

        exp_vals = [[3, 15, 5], [3, 12, 4], [2,6,3], [1,3,3], [1,2,2]]
        schema, results = self.planner.execute((n1, r, n2), None, None, orderby=[(('t', 'a'), 'DESC'), (('r', 'b'), 'DESC')])
        self.assertListEqual(results, exp_vals)
