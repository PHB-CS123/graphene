import unittest

from graphene.storage.base.array_store import *


class TestArrayStoreMethods(unittest.TestCase):
    def setUp(self):
        """
        Set up the GrapheneStore so that it writes datafiles to the testing
        directory
        """
        GrapheneStore.TESTING = True

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_empty_init(self):
        """
        Test that initializing an empty ArrayStore succeeds
        (file is opened successfully)
        """
        try:
            ArrayStore()
        except IOError:
            self.fail("ArrayStore initializer failed: "
                      "db file failed to open.")

    def test_double_init(self):
        """
        Test that initializing an empty ArrayStore succeeds when
        repeated; i.e. the old file is reopened and no errors occur.
        """
        try:
            ArrayStore()
        except IOError:
            self.fail("ArrayStore initializer failed: "
                      "db file failed to open.")
        try:
            ArrayStore()
        except IOError:
            self.fail("ArrayStore initializer failed on second attempt: "
                      "db file failed to open.")

    def test_invalid_init(self):
        """
        Test that initializing an ArrayStore with a non-multiple of 8
        raises an exception
        """
        with self.assertRaises(ValueError):
            ArrayStore(5)

    def test_invalid_write(self):
        """
        Test that writing a array to offset 0 raises an error
        """
        array_store = ArrayStore()

        empty_array = Array()
        with self.assertRaises(ValueError):
            array_store.write_item(empty_array)

    def test_invalid_read(self):
        """
        Test that reading a array from offset 0 raises an error
        """
        array_store = ArrayStore()

        with self.assertRaises(ValueError):
            array_store.item_at_index(0)

    def test_empty_read(self):
        """
        Make sure that reading an item when the file is empty returns None
        """
        array_store = ArrayStore()
        # Read an uncreated item
        no_item = array_store.item_at_index(1)
        # Make sure it returned None
        self.assertEquals(no_item, GeneralStore.EOF)

    def test_invalid_array_type(self):
        """
        Make sure that passing an invalid array type raises an error
        """
        with self.assertRaises(ValueError):
            ArrayStore.size_and_format_str_for_type(Property.PropertyType.int)

    def test_write_read_int_array(self):
        """
        Tests that the int array written to the ArrayStore is the
        same as the array read
        """
        array_store = ArrayStore()

        # Create an array and add it to the ArrayStore file
        array = Array(1, True, Property.PropertyType.intArray,
                      0, 3, 0, [2131243121, 824142142, 546543423])
        array_store.write_item(array)

        # Read the array from the ArrayStore file
        array_file = array_store.item_at_index(array.index)

        # Assert that the values are the same
        self.assertEquals(array, array_file)

        # Create a signed and add it to the ArrayStore file
        array = Array(1, True, Property.PropertyType.intArray,
                      0, 3, 0, [-2131243121, -824142142, -546543423])
        array_store.write_item(array)

        # Read the array from the ArrayStore file
        array_file = array_store.item_at_index(array.index)

        # Assert that the values are the same
        self.assertEquals(array, array_file)

    def test_write_read_long_array(self):
        """
        Tests that the long array written to the ArrayStore is the
        same as the array read
        """
        array_store = ArrayStore()

        # Create an array and add it to the ArrayStore file
        array = Array(1, True, Property.PropertyType.longArray,
                      0, 2, 0, [1717986918400, 1717986918401])
        array_store.write_item(array)

        # Read the array from the ArrayStore file
        array_file = array_store.item_at_index(array.index)

        # Assert that the values are the same
        self.assertEquals(array, array_file)

        # Create a signed array and add it to the ArrayStore file
        array = Array(1, True, Property.PropertyType.longArray,
                      0, 2, 0, [-1717986918400, -1717986918401])
        array_store.write_item(array)

        # Read the array from the ArrayStore file
        array_file = array_store.item_at_index(array.index)

        # Assert that the values are the same
        self.assertEquals(array, array_file)

    def test_write_read_bool_array(self):
        """
        Tests that the bool array written to the ArrayStore is the
        same as the array read
        """
        array_store = ArrayStore()

        # Create an array and add it to the ArrayStore file
        array = Array(1, True, Property.PropertyType.boolArray,
                      0, 5, 0, [True, False, False, True, True])
        array_store.write_item(array)

        # Read the array from the ArrayStore file
        array_file = array_store.item_at_index(array.index)

        # Assert that the values are the same
        self.assertEquals(array, array_file)

    def test_write_read_short_array(self):
        """
        Tests that the short array written to the ArrayStore is the
        same as the array read
        """
        array_store = ArrayStore()

        # Create an array and add it to the ArrayStore file
        array = Array(1, True, Property.PropertyType.shortArray,
                      0, 6, 0, [2, 8, 127, 32767, 0, 32764])
        array_store.write_item(array)

        # Read the array from the ArrayStore file
        array_file = array_store.item_at_index(array.index)

        # Assert that the values are the same
        self.assertEquals(array, array_file)

        # Create a signed array and add it to the ArrayStore file
        array = Array(1, True, Property.PropertyType.shortArray,
                      0, 6, 0, [-2, -8, -127, -32767, 0, -32764])
        array_store.write_item(array)

        # Read the array from the ArrayStore file
        array_file = array_store.item_at_index(array.index)

        # Assert that the values are the same
        self.assertEquals(array, array_file)

    def test_write_read_char_array(self):
        """
        Tests that the char array written to the ArrayStore is the
        same as the array read
        """
        array_store = ArrayStore()

        # Create an array and add it to the ArrayStore file
        array = Array(1, True, Property.PropertyType.charArray,
                      0, 8, 0, ["a", "b", "c", "d", "e", "f", "g", "h"])
        array_store.write_item(array)

        # Read the array from the ArrayStore file
        array_file = array_store.item_at_index(array.index)

        # Assert that the values are the same
        self.assertEquals(array, array_file)

        # Test unicode
        # Create a unicode array and add it to the ArrayStore file
        array = Array(1, True, Property.PropertyType.charArray,
                      0, 3, 0, [unichr(57344), unichr(57343), unichr(57342)])
        array_store.write_item(array)

        # Read the array from the ArrayStore file
        array_file = array_store.item_at_index(array.index)

        # Assert that the values are the same
        self.assertEquals(array, array_file)

    def test_write_read_float_array(self):
        """
        Tests that the float array written to the ArrayStore is the
        same as the array read
        """
        array_store = ArrayStore()

        # Create an array and add it to the ArrayStore file
        array = Array(1, True, Property.PropertyType.floatArray,
                      0, 4, 0, [3.14159, 2.71828, 0.333333, 2.64575131106])
        array_store.write_item(array)

        # Read the array from the ArrayStore file
        array_file = array_store.item_at_index(array.index)

        # Assert that the values are almost the same (floats are imprecise)
        self.assertTrue(array.almost_equal(array_file, 5))

        # Create a signed array and add it to the ArrayStore file
        array = Array(1, True, Property.PropertyType.floatArray,
                      0, 4, 0, [-3.14159, -2.71828, -0.333333, -2.64575131106])
        array_store.write_item(array)

        # Read the array from the ArrayStore file
        array_file = array_store.item_at_index(array.index)

        # Assert that the values are almost the same (floats are imprecise)
        self.assertTrue(array.almost_equal(array_file, 5))

    def test_write_read_double_array(self):
        """
        Tests that the float array written to the ArrayStore is the
        same as the array read
        """
        array_store = ArrayStore()

        # Create an array and add it to the ArrayStore file
        array = Array(1, True, Property.PropertyType.doubleArray,
                      0, 3, 0, [5e-324, 4e-325, 3e-326])
        array_store.write_item(array)

        # Read the array from the ArrayStore file
        array_file = array_store.item_at_index(array.index)

        # Assert that the values are the same
        self.assertEquals(array, array_file)

        # Create a signed array and add it to the ArrayStore file
        array = Array(1, True, Property.PropertyType.doubleArray,
                      0, 3, 0, [5e-324, 4e-325, 3e-326])
        array_store.write_item(array)

        # Read the array from the ArrayStore file
        array_file = array_store.item_at_index(array.index)

        # Assert that the values are the same
        self.assertEquals(array, array_file)

    def test_write_read_2_arrays(self):
        """
        Tests when 2 arrays are written after 1 array to the ArrayStore
        """
        array_store = ArrayStore()

        # Create one array and write it to the ArrayStore
        array1 = Array(1, True, Property.PropertyType.doubleArray,
                       0, 3, 0, [5e-324, 4e-325, 3e-326])
        array_store.write_item(array1)

        # Create 2 arrays and add them to the ArrayStore
        array2 = Array(2, True, Property.PropertyType.charArray,
                       0, 8, 0, ["a", "b", "c", "d", "e", "f", "g", "h"])
        array3 = Array(3, True, Property.PropertyType.charArray,
                       0, 3, 0, [unichr(57344), unichr(57343), unichr(57342)])
        array_store.write_item(array2)
        array_store.write_item(array3)

        # Read the properties from the ArrayStore file
        array1_file = array_store.item_at_index(array1.index)
        array2_file = array_store.item_at_index(array2.index)
        array3_file = array_store.item_at_index(array3.index)

        # Make sure their values are the same
        self.assertEquals(array1, array1_file)
        self.assertEquals(array2, array2_file)
        self.assertEquals(array3, array3_file)

    def test_overwrite_array(self):
        """
        Tests that overwriting an array in a database with 3 arrays works
        """
        array_store = ArrayStore()

        # Create 3 arrays
        array1 = Array(1, True, Property.PropertyType.doubleArray,
                       0, 3, 0, [5e-324, 4e-325, 3e-326])
        array2 = Array(2, True, Property.PropertyType.charArray,
                       0, 8, 0, ["a", "b", "c", "d", "e", "f", "g", "h"])
        array3 = Array(3, True, Property.PropertyType.charArray,
                       0, 3, 0, [unichr(57344), unichr(57343), unichr(57342)])

        # Write them to the array store
        array_store.write_item(array1)
        array_store.write_item(array2)
        array_store.write_item(array3)

        # Verify that they are in the store as expected
        array1_file = array_store.item_at_index(array1.index)
        self.assertEquals(array1, array1_file)

        array2_file = array_store.item_at_index(array2.index)
        self.assertEquals(array2, array2_file)

        array3_file = array_store.item_at_index(array3.index)
        self.assertEquals(array3, array3_file)

        # Create a new array2 and overwrite the old array2
        new_array2 = Array(2, True, Property.PropertyType.shortArray,
                           0, 6, 0, [2, 8, 127, 32767, 0, 32764])
        array_store.write_item(new_array2)

        # Verify that the data is still as expected
        array1_file = array_store.item_at_index(array1.index)
        self.assertEquals(array1, array1_file)

        new_array2_file = array_store.item_at_index(new_array2.index)
        self.assertEquals(new_array2, new_array2_file)

        array3_file = array_store.item_at_index(array3.index)
        self.assertEquals(array3, array3_file)

    def test_delete_array(self):
        """
        Tests that deleting 2 arrays in a database with 3 arrays works
        """
        array_store = ArrayStore()

        # Create 3 arrays
        array1 = Array(1, True, Property.PropertyType.doubleArray,
                       0, 3, 0, [5e-324, 4e-325, 3e-326])
        array2 = Array(2, True, Property.PropertyType.charArray,
                       0, 8, 0, ["a", "b", "c", "d", "e", "f", "g", "h"])
        array3 = Array(3, True, Property.PropertyType.charArray,
                       0, 3, 0, [unichr(57344), unichr(57343), unichr(57342)])

        # Write them to the array_store
        array_store.write_item(array1)
        array_store.write_item(array2)
        array_store.write_item(array3)

        # Verify that they are in the store as expected
        array1_file = array_store.item_at_index(array1.index)
        self.assertEquals(array1, array1_file)

        array2_file = array_store.item_at_index(array2.index)
        self.assertEquals(array2, array2_file)

        array3_file = array_store.item_at_index(array3.index)
        self.assertEquals(array3, array3_file)

        # Delete properties 1 and 3
        array_store.delete_item(array1)
        # Deleting from end of file, should return EOF when read
        array_store.delete_item(array3)

        # Verify deleted array is deleted
        del_array1_file = array_store.item_at_index(array1.index)
        self.assertIsNone(del_array1_file)

        # Verify unaffected array is as expected
        array2_file = array_store.item_at_index(array2.index)
        self.assertEquals(array2, array2_file)

        # Verify deleted array is deleted
        del_array3_file = array_store.item_at_index(array3.index)
        self.assertEquals(del_array3_file, EOF)
