import unittest

from graphene.commands import DeleteRelationCommand
from graphene.expressions import *
from graphene.storage import (StorageManager, GrapheneStore, Property, Relationship, Node)
from graphene.server.server import GrapheneServer
from graphene.utils.conversion import TypeConversion
from graphene.errors import TypeMismatchException
from graphene.traversal import Query
from graphene.query.planner import QueryPlanner
from graphene.storage.base.general_store import EOF
from graphene.utils.pretty_printer import PrettyPrinter

class TestDeleteRelationCommand(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True
        # Set to no colors to avoid escape sequences in output
        PrettyPrinter.TESTING = True

        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        self.server = GrapheneServer()
        self.sm = self.server.storage_manager
        self.node_manager = self.sm.node_manager

        self.node_type = self.sm.create_node_type("T", (("a", "int"),))
        self.other_node_type = self.sm.create_node_type("U", (("a", "int"),))
        self.rel_type = self.sm.create_relationship_type("R", (("a", "string"),))
        self.emp_rel_type = self.sm.create_relationship_type("S", (("a", "string"),))
        n1, p1 = self.sm.insert_node(self.node_type, ((Property.PropertyType.int, 1),))
        n2, p2 = self.sm.insert_node(self.node_type, ((Property.PropertyType.int, 2),))
        n3, p3 = self.sm.insert_node(self.node_type, ((Property.PropertyType.int, 3),))

        r1 = self.sm.insert_relation(self.rel_type,
            ((Property.PropertyType.string, "a"),), n1, n2)
        r2 = self.sm.insert_relation(self.rel_type,
            ((Property.PropertyType.string, "b"),), n2, n3)
        r3 = self.sm.insert_relation(self.rel_type,
            ((Property.PropertyType.string, "c"),), n3, n1)

        self.planner = QueryPlanner(self.sm)

        self.rel_schema = self.planner.get_schema([MatchRelation(None, "R")])
        self.emp_rel_schema = self.planner.get_schema([MatchRelation(None, "S")])

        self.node_schema = self.planner.get_schema([MatchNode(None, "T")])
        self.other_node_schema = self.planner.get_schema([MatchNode(None, "U")])

        self.empty_cmd = DeleteRelationCommand(None, None, None, None)

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        del self.sm
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def assertListEqualUnsorted(self, given, expected):
        self.assertListEqual(sorted(given), sorted(expected))

    def assertIsNoneOrEOF(self, item):
        """
        Since values at the end of a file are still nonexistent, both None and
        EOF are OK
        """
        self.assertTrue(item is None or item is EOF)

    def assertIsNotNoneOrEOF(self, item):
        """
        Since values at the end of a file are still nonexistent, both None and
        EOF are OK
        """
        self.assertFalse(item is None or item is EOF)

    def test_prop_dict(self):
        sch, props = (), ()
        expected = {}
        self.assertDictEqual(self.empty_cmd.get_prop_dict(sch, props), expected)

        sch, props = (('a', Property.PropertyType.int),), (1,)
        expected = {"a": (1, Property.PropertyType.int)}
        self.assertDictEqual(self.empty_cmd.get_prop_dict(sch, props), expected)

    def test_rel_iter(self):
        # Relation with no relations
        rel_data = (self.rel_schema, self.emp_rel_type, None)
        indices = map(lambda rel: rel.index, self.empty_cmd.rel_iter(self.sm, rel_data))
        self.assertListEqualUnsorted(indices, [])

        # Relation with empty schema
        rel_data = (self.rel_schema, self.rel_type, None)
        indices = map(lambda rel: rel.index, self.empty_cmd.rel_iter(self.sm, rel_data))
        self.assertListEqualUnsorted(indices, [1, 2, 3])

        # Relation with query that matches
        rel_data = (self.rel_schema, self.rel_type, Query(None,'a','=',"a"))
        indices = map(lambda rel: rel.index, self.empty_cmd.rel_iter(self.sm, rel_data))
        self.assertListEqualUnsorted(indices, [1])

        # Relation with query and no matches
        rel_data = (self.rel_schema, self.rel_type, Query(None,'a','=',"d"))
        indices = map(lambda rel: rel.index, self.empty_cmd.rel_iter(self.sm, rel_data))
        self.assertListEqualUnsorted(indices, [])

    def test_left_rel_iter(self):
        rel_data = (self.rel_schema, self.rel_type, None)

        # Relation not attached to these nodes
        node_data = (self.other_node_schema, self.other_node_type, None)
        indices = map(lambda rel: rel.index, self.empty_cmd.left_rel_iter(self.sm, rel_data, node_data))
        self.assertListEqualUnsorted(indices, [])

        # Relation attached to nodes (no restrictions)
        node_data = (self.node_schema, self.node_type, None)
        indices = map(lambda rel: rel.index, self.empty_cmd.left_rel_iter(self.sm, rel_data, node_data))
        self.assertListEqualUnsorted(indices, [1, 2, 3])

        # Relation attached to node (with matching query)
        node_data = (self.node_schema, self.node_type, Query(None, 'a', '=', 1))
        indices = map(lambda rel: rel.index, self.empty_cmd.left_rel_iter(self.sm, rel_data, node_data))
        self.assertListEqualUnsorted(indices, [1])

        # Relation attached to node (with non-matching query)
        node_data = (self.node_schema, self.node_type, Query(None, 'a', '=', 6))
        indices = map(lambda rel: rel.index, self.empty_cmd.left_rel_iter(self.sm, rel_data, node_data))
        self.assertListEqualUnsorted(indices, [])

    def test_right_rel_iter(self):
        rel_data = (self.rel_schema, self.rel_type, None)

        # Relation not attached to these nodes
        node_data = (self.other_node_schema, self.other_node_type, None)
        indices = map(lambda rel: rel.index, self.empty_cmd.right_rel_iter(self.sm, rel_data, node_data))
        self.assertListEqualUnsorted(indices, [])

        # Relation attached to nodes (no restrictions)
        node_data = (self.node_schema, self.node_type, None)
        indices = map(lambda rel: rel.index, self.empty_cmd.right_rel_iter(self.sm, rel_data, node_data))
        self.assertListEqualUnsorted(indices, [1, 2, 3])

        # Relation attached to node (with matching query)
        node_data = (self.node_schema, self.node_type, Query(None, 'a', '=', 1))
        indices = map(lambda rel: rel.index, self.empty_cmd.right_rel_iter(self.sm, rel_data, node_data))
        self.assertListEqualUnsorted(indices, [3])

        # Relation attached to node (with non-matching query)
        node_data = (self.node_schema, self.node_type, Query(None, 'a', '=', 6))
        indices = map(lambda rel: rel.index, self.empty_cmd.right_rel_iter(self.sm, rel_data, node_data))
        self.assertListEqualUnsorted(indices, [])

    def test_both_rel_iter(self):
        rel_data = (self.rel_schema, self.rel_type, None)

        # Relation not attached to these nodes
        left_data = (self.other_node_schema, self.other_node_type, None)
        right_data = (self.node_schema, self.node_type, None)
        indices = map(lambda rel: rel.index, self.empty_cmd.both_rel_iter(self.sm, rel_data, left_data, right_data))
        self.assertListEqualUnsorted(indices, [])

        left_data = (self.node_schema, self.node_type, None)
        right_data = (self.other_node_schema, self.other_node_type, None)
        indices = map(lambda rel: rel.index, self.empty_cmd.both_rel_iter(self.sm, rel_data, left_data, right_data))
        self.assertListEqualUnsorted(indices, [])

        # Relation with queries on left
        left_data = (self.node_schema, self.node_type, Query(None, 'a', '=', 1))
        right_data = (self.node_schema, self.node_type, None)
        indices = map(lambda rel: rel.index, self.empty_cmd.both_rel_iter(self.sm, rel_data, left_data, right_data))
        self.assertListEqualUnsorted(indices, [1])

        # Relation with queries on right
        left_data = (self.node_schema, self.node_type, None)
        right_data = (self.node_schema, self.node_type, Query(None, 'a', '=', 1))
        indices = map(lambda rel: rel.index, self.empty_cmd.both_rel_iter(self.sm, rel_data, left_data, right_data))
        self.assertListEqualUnsorted(indices, [3])

    def test_execute_relation_only(self):
        cmd = DeleteRelationCommand("R", None, None, None)
        cmd.execute(self.sm)

        # Check that all relations were deleted
        self.assertIsNoneOrEOF(self.sm.relprop[1])
        self.assertIsNoneOrEOF(self.sm.relprop[2])
        self.assertIsNoneOrEOF(self.sm.relprop[3])

    def test_execute_with_rel_query(self):
        cmd = DeleteRelationCommand("R", (((None, 'a'), '=', '"a"'),), None, None)
        cmd.execute(self.sm)

        # Check that all relations were deleted
        self.assertIsNoneOrEOF(self.sm.relprop[1])
        self.assertIsNotNoneOrEOF(self.sm.relprop[2])
        self.assertIsNotNoneOrEOF(self.sm.relprop[3])

    def test_execute_left_node(self):
        cmd = DeleteRelationCommand("R", None, ("T", None), None)
        cmd.execute(self.sm)

        # Check that all relations were deleted
        self.assertIsNoneOrEOF(self.sm.relprop[1])
        self.assertIsNoneOrEOF(self.sm.relprop[2])
        self.assertIsNoneOrEOF(self.sm.relprop[3])

    def test_execute_right_node(self):
        cmd = DeleteRelationCommand("R", None, None, ("T", None))
        cmd.execute(self.sm)

        # Check that all relations were deleted
        self.assertIsNoneOrEOF(self.sm.relprop[1])
        self.assertIsNoneOrEOF(self.sm.relprop[2])
        self.assertIsNoneOrEOF(self.sm.relprop[3])

    def test_execute_left_node_with_query(self):
        cmd = DeleteRelationCommand("R", None, ("T", (((None, 'a'), '=', '1'),)), None)
        cmd.execute(self.sm)

        # Check that all relations were deleted
        self.assertIsNoneOrEOF(self.sm.relprop[1])
        self.assertIsNotNoneOrEOF(self.sm.relprop[2])
        self.assertIsNotNoneOrEOF(self.sm.relprop[3])

    def test_execute_right_node_with_query(self):
        cmd = DeleteRelationCommand("R", None, None, ("T", (((None, 'a'), '=', '1'),)))
        cmd.execute(self.sm)

        # Check that all relations were deleted
        self.assertIsNotNoneOrEOF(self.sm.relprop[1])
        self.assertIsNotNoneOrEOF(self.sm.relprop[2])
        self.assertIsNoneOrEOF(self.sm.relprop[3])

    def test_execute_both_node(self):
        cmd = DeleteRelationCommand("R", None, ("T", None), ("T", None))
        cmd.execute(self.sm)

        # Check that all relations were deleted
        self.assertIsNoneOrEOF(self.sm.relprop[1])
        self.assertIsNoneOrEOF(self.sm.relprop[2])
        self.assertIsNoneOrEOF(self.sm.relprop[3])

    def test_execute_both_node_one_side_wrong(self):
        cmd = DeleteRelationCommand("R", None, ("T", None), ("U", None))
        cmd.execute(self.sm)

        # Check that all relations were deleted
        self.assertIsNotNoneOrEOF(self.sm.relprop[1])
        self.assertIsNotNoneOrEOF(self.sm.relprop[2])
        self.assertIsNotNoneOrEOF(self.sm.relprop[3])
