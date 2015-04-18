import unittest

from graphene.storage.general_type_type import *


class TestGeneralTypeTypeMethods(unittest.TestCase):
    def test_empty_init(self):
        """
        Tests that initializing a GeneralTypeType with no arguments, uses the
        default values below.
        """
        type_t = GeneralTypeType()
        self.assertEquals(type_t.index, 0)
        self.assertEquals(type_t.inUse, True)
        self.assertEquals(type_t.typeName, 0)
        self.assertEquals(type_t.propertyType.value, 0)
        self.assertEquals(type_t.nextType, 0)

    def test_init(self):
        """
        Tests that initializing a GeneralTypeType with a set of values stores
        those values properly
        """
        type_t = GeneralTypeType(32, False, 42, 21, 30)
        self.assertEquals(type_t.index, 32)
        self.assertEquals(type_t.inUse, False)
        self.assertEquals(type_t.typeName, 42)
        self.assertEquals(type_t.propertyType, 21)
        self.assertEquals(type_t.nextType, 30)

    def test_eq(self):
        """
        Tests that == operator returns True when two types are equal
        and False when they are not
        """
        type_t1 = GeneralTypeType(32, False, 42, 21, 30)
        type_t2 = GeneralTypeType(32, False, 42, 21, 30)
        type_t3 = GeneralTypeType(12, True, 24, 36, 48)

        self.assertTrue(type_t1 == type_t2)
        self.assertFalse(type_t1 == type_t3)
        self.assertFalse(type_t2 == type_t3)
        self.assertFalse(type_t1 == 1)

