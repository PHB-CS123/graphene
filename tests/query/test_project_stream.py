import unittest

from graphene.server.server import GrapheneServer
from graphene.query.project_stream import ProjectStream
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.expressions import *
from graphene.errors import *
from graphene.traversal import Query

class TestProjectStream(unittest.TestCase):
    def test_all_identified_no_project(self):
        results = [[1,2,3], [4,5,6], [7,8,9]]
        schema = (("t.a", Property.PropertyType.int),
            ("t.b", Property.PropertyType.int),
            ("t.c", Property.PropertyType.int))
        stream = ProjectStream((), schema, results)
        self.assertListEqual(list(stream), results)

    def test_all_identified_with_project(self):
        results = [[1,2,3], [4,5,6], [7,8,9]]
        schema = (("t.a", Property.PropertyType.int),
            ("t.b", Property.PropertyType.int),
            ("t.c", Property.PropertyType.int))

        ## identified
        # single project
        expected = [[1],[4],[7]]
        stream = ProjectStream((("t", "a"),), schema, results)
        self.assertListEqual(list(stream), expected)
        self.assertListEqual(stream.schema_names, ["t.a"])

        # multiple project
        expected = [[1,3],[4,6],[7,9]]
        stream = ProjectStream((("t", "a"),("t", "c")), schema, results)
        self.assertListEqual(list(stream), expected)
        self.assertListEqual(stream.schema_names, ["t.a", "t.c"])

        # out of order
        expected = [[2,1],[5,4],[8,7]]
        stream = ProjectStream((("t", "b"),("t", "a")), schema, results)
        self.assertListEqual(list(stream), expected)
        self.assertListEqual(stream.schema_names, ["t.b", "t.a"])

        ## unidentified
        # single project
        expected = [[1],[4],[7]]
        stream = ProjectStream(((None, "a"),), schema, results)
        self.assertListEqual(list(stream), expected)
        self.assertListEqual(stream.schema_names, ["a"])

        # multiple project
        expected = [[1,2],[4,5],[7,8]]
        stream = ProjectStream(((None, "a"),(None, "b")), schema, results)
        self.assertListEqual(list(stream), expected)
        self.assertListEqual(stream.schema_names, ["a", "b"])

        # out of order
        expected = [[2,1],[5,4],[8,7]]
        stream = ProjectStream(((None, "b"),(None, "a")), schema, results)
        self.assertListEqual(list(stream), expected)
        self.assertListEqual(stream.schema_names, ["b", "a"])

    def test_unidentified(self):
        results = [[1,2,3], [4,5,6], [7,8,9]]
        expected = [[1,3], [4,6], [7,9]]
        schema = (("t.a", Property.PropertyType.int),
            ("b", Property.PropertyType.int),
            ("t.c", Property.PropertyType.int))

        stream = ProjectStream((), schema, results)
        self.assertListEqual(list(stream), expected)
        self.assertListEqual(stream.schema_names, ["t.a", "t.c"])

    def test_ambiguous(self):
        results = [[1,2,3], [4,5,6], [7,8,9]]
        schema = (("t.a", Property.PropertyType.int),
            ("r.b", Property.PropertyType.int),
            ("t2.a", Property.PropertyType.int))

        # Ambiguousness is determined in index generation
        with self.assertRaises(AmbiguousPropertyException):
            stream = ProjectStream(((None, "a"),), schema, results)

    def test_nonexistent(self):
        results = [[1,2,3], [4,5,6], [7,8,9]]
        schema = (("t.a", Property.PropertyType.int),
            ("r.b", Property.PropertyType.int),
            ("t2.a", Property.PropertyType.int))

        # nonexistent property name
        with self.assertRaises(NonexistentPropertyException):
            stream = ProjectStream(((None, "g"),), schema, results)

        # nonexistent identifier
        with self.assertRaises(NonexistentPropertyException):
            stream = ProjectStream((("q", "a"),), schema, results)
