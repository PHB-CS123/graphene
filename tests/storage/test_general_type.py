import unittest

from graphene.storage.general_type import *


class TestGeneralTypeMethods(unittest.TestCase):
    def test_empty_init(self):
        """
        Tests that initializing a Node with no arguments, uses the
        default values below.
        """
        node = GeneralType()
        self.assertEquals(node.index, 0)
        self.assertEquals(node.inUse, True)
        self.assertEquals(node.nameId, 0)
        self.assertEquals(node.firstType, 0)

    def test_init(self):
        """
        Tests that initializing a Node with a set of values stores
        those values properly
        """
        node = GeneralType(32, False, 42, 21)
        self.assertEquals(node.index, 32)
        self.assertEquals(node.inUse, False)
        self.assertEquals(node.nameId, 42)
        self.assertEquals(node.firstType, 21)

    def test_eq(self):
        """
        Tests that == operator returns True when two nodes are equal
        and False when they are not
        """
        node1 = GeneralType(32, False, 42, 21)
        node2 = GeneralType(32, False, 42, 21)
        node3 = GeneralType(15, True, 12, 18)

        self.assertTrue(node1 == node2)
        self.assertFalse(node1 == node3)
        self.assertFalse(node2 == node3)
        self.assertFalse(node1 == 1)
