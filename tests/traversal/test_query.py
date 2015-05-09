import unittest

from graphene.server.server import GrapheneServer
from graphene.query.planner import QueryPlanner
from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.expressions import *
from graphene.errors import *
from graphene.traversal import Query

class TestQuery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        GrapheneStore.TESTING = True
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        cls.sm = StorageManager()

    @classmethod
    def tearDownClass(cls):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_equality(self):
        q1 = Query('t', 'a', '=', 1)
        q2 = Query('t', 'a', '=', 1)
        self.assertEqual(q1, q2)
        self.assertFalse(q1 == 5)

    def test_inequality(self):
        q1 = Query(None, 'a', '=', 1)
        q2 = Query('t', 'a', '=', 1)
        self.assertNotEqual(q1, q2)

    def test_test(self):
        prop_dict = {'t.a': (1, Property.PropertyType.int)}

        q = Query('t', 'a', '=', 1)
        self.assertTrue(q.test(prop_dict))

        q = Query('t', 'a', '>', 1)
        self.assertFalse(q.test(prop_dict))

        q = Query('t', 'a', '<', 1)
        self.assertFalse(q.test(prop_dict))

        q = Query('t', 'a', '>=', 0)
        self.assertTrue(q.test(prop_dict))

        q = Query('t', 'a', '<=', 0)
        self.assertFalse(q.test(prop_dict))

        q = Query('t', 'a', '!=', 1)
        self.assertFalse(q.test(prop_dict))

        q = Query('t', 'a', '!!', 1)
        self.assertFalse(q.test(prop_dict))

        q = Query('t', 'b', '!=', 1)
        with self.assertRaises(NonexistentPropertyException):
            q.test(prop_dict)

    def test_parse_chain(self):
        schema = (('t.a', Property.PropertyType.int),('t.b', Property.PropertyType.int))

        chain = (('t','a','=','1'),)
        self.assertEqual(Query.parse_chain(self.sm, chain, schema), Query('t','a','=', 1))

        # This will be changed later when we actually care about booleans
        chain = (('t','a','=','1'),'AND',('t','b','>','0'))
        self.assertEqual(Query.parse_chain(self.sm, chain, schema),
            AndOperator([Query('t','a','=', 1), Query('t','b','>', 0)]))

        chain = (('t','c','>','0'),)
        with self.assertRaises(NonexistentPropertyException):
            Query.parse_chain(self.sm, chain, schema)
