import unittest

from graphene.traversal import Query
from graphene.storage import Property
from graphene.expressions import OrOperator

class TestOrOperator(unittest.TestCase):
    def test_test(self):
        q1, q2 = Query("t", "a", "=", 1), Query("t", "b", "=", 2)
        op = OrOperator([q1, q2])

        self.assertTrue(op.test({"t.a": (1, Property.PropertyType.int),
                                 "t.b": (2, Property.PropertyType.int)}))

        self.assertTrue(op.test({"t.a": (3, Property.PropertyType.int),
                                  "t.b": (2, Property.PropertyType.int)}))

        self.assertTrue(op.test({"t.a": (1, Property.PropertyType.int),
                                  "t.b": (4, Property.PropertyType.int)}))

        self.assertFalse(op.test({"t.a": (3, Property.PropertyType.int),
                                  "t.b": (4, Property.PropertyType.int)}))

    def test_eq(self):
        q1 = Query("t", "a", "=", 1)
        q2 = Query("t", "b", "=", 2)
        q3 = Query("t", "c", "<", 4)

        self.assertTrue(OrOperator([q1, q2]) == OrOperator([q1, q2]))
        self.assertFalse(OrOperator([q1, q2]) == OrOperator([q1, q3]))
        self.assertFalse(OrOperator([q1, q2]) == 5)
        self.assertTrue(OrOperator([q1, q2]) != 5)

    def test_schema(self):
        q1, q2 = Query("t", "a", "=", 1), Query("t", "b", "=", 2)
        op = OrOperator([q1, q2])

        self.assertEqual(set(["t.a", "t.b"]), op.schema)
