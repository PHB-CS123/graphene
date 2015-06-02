import unittest

from graphene.storage.base.array import *


class TestArrayMethods(unittest.TestCase):
    def test_empty_init(self):
        """
        Tests that initializing a array with no arguments, uses the
        default values below.
        """
        array = Array()

        self.assertEquals(array.index, 0)
        self.assertEquals(array.inUse, True)
        self.assertEquals(array.type, Property.PropertyType.undefined)
        self.assertEquals(array.previousBlock, 0)
        self.assertEquals(array.amount, 0)
        self.assertEquals(array.blocks, 0)
        self.assertEquals(array.nextBlock, 0)
        self.assertIsNone(array.items)

    def test_init(self):
        """
        Tests that initializing an array with a set of values stores
        those values properly
        """
        # Array values
        index = 1
        in_use = False
        array_type = Property.PropertyType.intArray
        previous_block = 2
        amount = 5
        blocks = 1
        next_block = 4
        items = [5, 4, 3, 2, 1]

        # Create array
        array = Array(index, in_use, array_type, previous_block,
                      amount, blocks, next_block, items)

        # Check values
        self.assertEquals(array.index, index)
        self.assertEquals(array.inUse, in_use)
        self.assertEquals(array.type, array_type)
        self.assertEquals(array.previousBlock, previous_block)
        self.assertEquals(array.amount, amount)
        self.assertEquals(array.blocks, blocks)
        self.assertEquals(array.nextBlock, next_block)
        self.assertEquals(array.items, items)

    def test_eq(self):
        """
        Tests that the == operator returns True when two properties are equal
        and False when they are not. Tests != when checking not equals.
        """
        array1 = Array(1, True, Property.PropertyType.intArray, 2, 3, 4, 5,
                       [1, 2, 3])
        array2 = Array(1, True, Property.PropertyType.intArray, 2, 3, 4, 5,
                       [1, 2, 3])
        array3 = Array(9, False, Property.PropertyType.boolArray, 5, 4, 1, 8,
                       [True, False, False, True])

        self.assertEqual(array1, array2)
        self.assertNotEqual(array1, array3)
        self.assertNotEqual(array2, array3)
        self.assertNotEqual(array1, 1)

    def test_almost_equal(self):
        """
        Tests that the almost equal method returns True when two items are
        almost equal within a precision factor, and false otherwise.
        """
        array1 = Array(1, True, Property.PropertyType.floatArray, 2, 3, 4, 5,
                       [3.14159, 2.71828, 0.33333, 2.64575])
        array2 = Array(1, True, Property.PropertyType.floatArray, 2, 3, 4, 5,
                       [3.14159011, 2.7182800, 0.33333298, 2.6457512])
        array3 = Array(9, False, Property.PropertyType.floatArray, 5, 4, 8, 7,
                       [True, False, False, True])

        self.assertTrue(array1.almost_equal(array2, 5))
        self.assertFalse(array1.almost_equal(array2, 6))
        self.assertFalse(array2.almost_equal(array3, 3))
        self.assertFalse(array1.almost_equal(1, 6))