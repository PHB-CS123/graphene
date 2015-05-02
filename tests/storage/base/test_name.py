import unittest

from graphene.storage.base.name import *


class TestNameMethods(unittest.TestCase):
    def test_empty_init(self):
        """
        Tests that initializing a Name with no arguments, uses the
        default values below.
        """
        name_data = Name()
        self.assertEquals(name_data.index, 0)
        self.assertEquals(name_data.inUse, True)
        self.assertEquals(name_data.previousBlock, 0)
        self.assertEquals(name_data.length, 0)
        self.assertEquals(name_data.nextBlock, 0)
        self.assertEquals(name_data.name, '')

    def test_init(self):
        """
        Tests that initializing a Name with a set of values stores
        those values properly
        """
        name_data = Name(32, False, 42, 3, 82, "Hello there, I'm a long str")
        self.assertEquals(name_data.index, 32)
        self.assertEquals(name_data.inUse, False)
        self.assertEquals(name_data.previousBlock, 42)
        self.assertEquals(name_data.length, 3)
        self.assertEquals(name_data.nextBlock, 82)
        self.assertEquals(name_data.name, "Hello there, I'm a long str")

    def test_eq(self):
        """
        Tests that == operator returns True when two nodes are equal
        and False when they are not. Tests != when checking not equals.
        """
        name_data1 = Name(32, False, 42, 3, 82, "Hello there, I'm a long str")
        name_data2 = Name(32, False, 42, 3, 82, "Hello there, I'm a long str")
        name_data3 = Name(2, True, 20, 1, 40, "Hello")

        self.assertEqual(name_data1, name_data2)
        self.assertNotEqual(name_data1, name_data3)
        self.assertNotEqual(name_data2, name_data3)
        self.assertNotEqual(name_data1, 1)

