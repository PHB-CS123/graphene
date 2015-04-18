import unittest

from graphene.storage.general_type import *


class TestGeneralTypeMethods(unittest.TestCase):
    def test_empty_init(self):
        """
        Tests that initializing a GeneralType with no arguments, uses the
        default values below.
        """
        gen_type = GeneralType()
        self.assertEquals(gen_type.index, 0)
        self.assertEquals(gen_type.inUse, True)
        self.assertEquals(gen_type.nameId, 0)
        self.assertEquals(gen_type.firstType, 0)

    def test_init(self):
        """
        Tests that initializing a GeneralType with a set of values stores
        those values properly
        """
        gen_type = GeneralType(32, False, 42, 21)
        self.assertEquals(gen_type.index, 32)
        self.assertEquals(gen_type.inUse, False)
        self.assertEquals(gen_type.nameId, 42)
        self.assertEquals(gen_type.firstType, 21)

    def test_eq(self):
        """
        Tests that == operator returns True when two types are equal
        and False when they are not
        """
        gen_type1 = GeneralType(32, False, 42, 21)
        gen_type2 = GeneralType(32, False, 42, 21)
        gen_type3 = GeneralType(15, True, 12, 18)

        self.assertTrue(gen_type1 == gen_type2)
        self.assertFalse(gen_type1 == gen_type3)
        self.assertFalse(gen_type2 == gen_type3)
        self.assertFalse(gen_type1 == 1)
