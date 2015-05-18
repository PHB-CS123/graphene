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

    def test_reduce_operators(self):
        q = Query('t', 'a', '=', 1)
        self.assertEqual(Query.reduce_operators(q), q)

        q = AndOperator([Query('t', 'a', '=', 1), Query('t', 'a', '=', 2)])
        self.assertEqual(Query.reduce_operators(q), q)

        q = OrOperator([Query('t', 'a', '=', 1), Query('t', 'a', '=', 2)])
        self.assertEqual(Query.reduce_operators(q), q)

        q = (Query('t', 'a', '=', 1), 'AND', Query('t', 'a', '=', 2))
        self.assertEqual(Query.reduce_operators(q),
            AndOperator([Query('t', 'a', '=', 1), Query('t', 'a', '=', 2)]))

        q = (Query('t', 'a', '=', 1), 'OR', Query('t', 'a', '=', 2))
        self.assertEqual(Query.reduce_operators(q),
            OrOperator([Query('t', 'a', '=', 1), Query('t', 'a', '=', 2)]))

        q = (Query('t', 'a', '=', 1), 'OR', [ Query('t', 'a', '=', 2), 'OR', Query('t', 'a', '=', 3)])
        self.assertEqual(Query.reduce_operators(q),
            OrOperator([Query('t', 'a', '=', 1), OrOperator([Query('t', 'a', '=', 2), Query('t', 'a', '=', 3)])]))

        q = (Query('t', 'a', '=', 1), 'AND', Query('t', 'a', '=', 2), 'OR', Query('t', 'a', '=', 3))
        self.assertEqual(Query.reduce_operators(q),
            OrOperator([AndOperator([Query('t', 'a', '=', 1), Query('t', 'a', '=', 2)]), Query('t', 'a', '=', 3)]))

        q = []
        self.assertEqual(Query.reduce_operators(q), [])

    def test_parse_chain(self):
        schema = (('t.a', Property.PropertyType.int),('t.b', Property.PropertyType.int))

        chain = (('t','a','=','1'),)
        self.assertEqual(Query.parse_chain(self.sm, chain, schema), Query('t','a','=', 1))

        # Booleans
        chain = (('t','a','=','1'),'AND',('t','b','>','0'))
        self.assertEqual(Query.parse_chain(self.sm, chain, schema),
            AndOperator([Query('t','a','=', 1), Query('t','b','>', 0)]))

        chain = (('t','a','=','1'),'OR',('t','b','>','0'))
        self.assertEqual(Query.parse_chain(self.sm, chain, schema),
            OrOperator([Query('t','a','=', 1), Query('t','b','>', 0)]))

        # Bad property
        chain = (('t','c','>','0'),)
        with self.assertRaises(NonexistentPropertyException):
            Query.parse_chain(self.sm, chain, schema)

        # Test parens
        chain = (('t','a','=','1'),'OR',('t','b','>','0'),'AND',('t','b','<','3'))
        self.assertEqual(Query.parse_chain(self.sm, chain, schema),
            OrOperator([Query('t','a','=', 1), AndOperator([Query('t','b','>', 0), Query('t','b','<', 3)])]))

        chain = ('(',('t','a','=','1'),'OR',('t','b','>','0'),')','AND',('t','b','<','3'))
        self.assertEqual(Query.parse_chain(self.sm, chain, schema),
            AndOperator([OrOperator([Query('t','a','=', 1), Query('t','b','>', 0)]), Query('t','b','<', 3)]))

        # Test uneven parens
        chain = ('(',('t','a','=','1'),'OR',('t','b','>','0'),')','AND',('t','b','<','3'),')')
        with self.assertRaises(ValueError):
            Query.parse_chain(self.sm, chain, schema)

        chain = ('(','(',('t','a','=','1'),'OR',('t','b','>','0'),')','AND',('t','b','<','3'))
        with self.assertRaises(ValueError):
            Query.parse_chain(self.sm, chain, schema)

