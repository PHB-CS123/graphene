import unittest

from graphene.storage.intermediate.general_array_manager import *
from random import randint, uniform

class TestGeneralArrayManagerMethods(unittest.TestCase):
    # This block size should be a multiple of 8, should work for any valid size
    TEST_BLOCK_SIZE = 32
    # Can be any positive value, should not be small to avoid fragmentation
    TEST_STRING_BLOCK_SIZE = 15

    def setUp(self):
        GrapheneStore.TESTING = True

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_init(self):
        """
        Test that initializing a GeneralArrayManager succeeds (file is opened)
        """
        try:
            GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                self.TEST_STRING_BLOCK_SIZE)
        except IOError:
            self.fail("GeneralArrayManager initializer failed: %s"
                      "db file failed to open.")

    def test_double_init(self):
        """
        Test that initializing a GeneralArrayManager succeeds when repeated;
        i.e. the old file is reopened and no errors occur.
        """
        try:
            GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                self.TEST_STRING_BLOCK_SIZE)
        except IOError:
            self.fail("GeneralArrayManager initializer failed: %s"
                      "db file failed to open.")
        try:
            GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                self.TEST_STRING_BLOCK_SIZE)
        except IOError:
            self.fail("GeneralArrayManager initializer failed on second"
                      "attempt: %s db file failed to open.")

    def test_eof_read(self):
        """
        Test that reading from an empty file returns an EOF
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)
        result = array_manager.read_array_at_index(1)
        self.assertEquals(result, EOF)

    def test_write_read_array_1_block(self):
        """
        Test that writing an array that spans a single block works as expected
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Number of items in an array with the current block size
        array_size = self.TEST_BLOCK_SIZE / 4
        # Random number of items
        rand_size = randint(0, array_size - 1)
        # Create an array and add it to the GeneralArrayStore
        array = [randint(-2**31, 2**31 - 1) for _ in range(0, rand_size + 1)]
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.intArray)

        # Read it back from the array manager
        array_file = array_manager.read_array_at_index(array_idx)
        # Make sure they are the same
        self.assertEqual(array, array_file)

    def test_write_read_empty_array(self):
        """
        Test that writing an int array that spans multiple blocks works as
        expected
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Create an array and add it to the GeneralArrayStore
        array = []
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.intArray)

        # Read it back from the array manager
        array_file = array_manager.read_array_at_index(array_idx)
        # Make sure they are the same
        self.assertEqual(array, array_file)

    def test_write_read_int_array(self):
        """
        Test that writing an int array that spans multiple blocks works as
        expected
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Number of items in an array with the current block size
        array_size = self.TEST_BLOCK_SIZE / 4
        # Random number of items
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        # Create an array and add it to the GeneralArrayStore
        array = [randint(-2**31, 2**31 - 1) for _ in range(0, rand_size + 1)]
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.intArray)

        # Read it back from the array manager
        array_file = array_manager.read_array_at_index(array_idx)
        # Make sure they are the same
        self.assertEqual(array, array_file)

    def test_write_read_long_array(self):
        """
        Test that writing a long array that spans multiple blocks works as
        expected
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Number of items in an array with the current block size
        array_size = self.TEST_BLOCK_SIZE / 8
        # Random number of items
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        # Create an array and add it to the GeneralArrayStore
        array = [randint(-2**63, 2**63 - 1) for _ in range(0, rand_size + 1)]
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.longArray)

        # Read it back from the array manager
        array_file = array_manager.read_array_at_index(array_idx)
        # Make sure they are the same
        self.assertEqual(array, array_file)

    def test_write_read_bool_array(self):
        """
        Test that writing a bool array that spans multiple blocks works as
        expected
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Number of items in an array with the current block size
        array_size = self.TEST_BLOCK_SIZE
        # Random number of items
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        # Create an array and add it to the GeneralArrayStore
        array = [bool(randint(0, 1)) for _ in range(0, rand_size + 1)]
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.boolArray)

        # Read it back from the array manager
        array_file = array_manager.read_array_at_index(array_idx)
        # Make sure they are the same
        self.assertEqual(array, array_file)

    def test_write_read_short_array(self):
        """
        Test that writing a short array that spans multiple blocks works as
        expected
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Number of items in an array with the current block size
        array_size = self.TEST_BLOCK_SIZE / 2
        # Random number of items
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        # Create an array and add it to the GeneralArrayStore
        array = [randint(-2**15, 2**15 - 1) for _ in range(0, rand_size + 1)]
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.shortArray)

        # Read it back from the array manager
        array_file = array_manager.read_array_at_index(array_idx)
        # Make sure they are the same
        self.assertEqual(array, array_file)

    def test_write_read_char_array(self):
        """
        Test that writing a char array that spans multiple blocks works as
        expected
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Number of items in an array with the current block size
        array_size = self.TEST_BLOCK_SIZE / 2
        # Random number of items
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        # Create an array and add it to the GeneralArrayStore
        array = [unichr(randint(0, 2**16 - 1)) for _ in range(0, rand_size + 1)]
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.charArray)

        # Read it back from the array manager
        array_file = array_manager.read_array_at_index(array_idx)
        # Make sure they are the same
        self.assertEqual(array, array_file)

    def test_write_read_float_array(self):
        """
        Test that writing a float array that spans multiple blocks works as
        expected
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Number of items in an array with the current block size
        array_size = self.TEST_BLOCK_SIZE / 4
        # Random number of items
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        # Create an array and add it to the GeneralArrayStore
        array = [uniform(-10, 10) for _ in range(0, rand_size + 1)]
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.floatArray)

        # Read it back from the array manager
        array_file = array_manager.read_array_at_index(array_idx)
        # Make sure they are almost the same (float imprecise)
        almost_equal_array = lambda x, y: self.assertAlmostEqual(x, y, 5)
        map(almost_equal_array, array, array_file)

    def test_write_read_double_array(self):
        """
        Test that writing a double array that spans multiple blocks works as
        expected
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Number of items in an array with the current block size
        array_size = self.TEST_BLOCK_SIZE / 8
        # Random number of items
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        # Create an array and add it to the GeneralArrayStore
        array = [uniform(-10, 10) for _ in range(0, rand_size + 1)]
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.doubleArray)

        # Read it back from the array manager
        array_file = array_manager.read_array_at_index(array_idx)
        # Make sure they are the same
        self.assertEqual(array, array_file)

    def test_write_read_string_array(self):
        """
        Test that writing a string array that spans multiple blocks works as
        expected
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Number of items in an array with the current block size
        array_size = self.TEST_BLOCK_SIZE / 2
        # String block size (shorter name)
        str_size = self.TEST_STRING_BLOCK_SIZE
        # Random number of items
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        rand_str_size = randint(1, 3) * str_size + randint(0, str_size - 1)
        # Create an array and add it to the GeneralArrayStore
        array = [rand_str_size * "D" for _ in range(0, rand_size + 1)]
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.stringArray)

        # Read it back from the array manager
        array_file = array_manager.read_array_at_index(array_idx)
        # Make sure they are the same
        self.assertEqual(array, array_file)

    def test_mangled_return_none(self):
        """
        Test that when reading a mangled array, the method returns None.
        Assuming the mangling is not at the end of the file
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Create an arbitrary int array
        array_size = self.TEST_BLOCK_SIZE / 4
        rand_size = randint(2, 4) * array_size + randint(0, array_size - 1)
        array = [randint(-2**31, 2**31 - 1) for _ in range(0, rand_size + 1)]
        # Write it to the array manager
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.intArray)

        # Mangle the array by deleting from the 2nd block (first block intact)
        array_manager.storeManager.delete_item_at_index(array_idx + 1)

        # Make sure that the read_name_at_index method returns None or EOF
        result = array_manager.read_array_at_index(array_idx)
        self.assertTrue(result is None or result is EOF)

    def test_mangled_return_EOF(self):
        """
        Test that when reading a mangled array, the method returns None.
        Assuming the mangling is at the end of the file (the file is truncated)
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Create an arbitrary int array
        array_size = self.TEST_BLOCK_SIZE / 4
        rand_size = array_size + randint(0, array_size - 1)
        array = [randint(-2**31, 2**31 - 1) for _ in range(0, rand_size + 1)]
        # Write it to the array manager
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.intArray)

        # Mangle the array by deleting from the 2nd block (first block intact)
        array_manager.storeManager.delete_item_at_index(array_idx + 1)

        # Make sure that the read_name_at_index method returns None or EOF
        result = array_manager.read_array_at_index(array_idx)
        self.assertTrue(result is None or result is EOF)

    def test_invalid_delete(self):
        """
        Test that deleting an array at a non-starting index throws an error
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Create an arbitrary int array
        array_size = self.TEST_BLOCK_SIZE / 4
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        array = [randint(-2**31, 2**31 - 1) for _ in range(0, rand_size + 1)]
        # Write it to the array manager
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.intArray)

        # Try to mangle the array and expect an index error
        with self.assertRaises(IndexError):
            array_manager.delete_array_at_index(array_idx + 1)

    def test_mangled_delete(self):
        """
        Test that when deleting a mangled array, the method returns
        an error (false)
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)

        # Create an arbitrary int array
        array_size = self.TEST_BLOCK_SIZE / 4
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        array = [randint(-2**31, 2**31 - 1) for _ in range(0, rand_size + 1)]
        # Write it to the array manager
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.intArray)

        # Mangle the array by deleting from the 2nd block (first block intact)
        array_manager.storeManager.delete_item_at_index(array_idx + 1)
        # Make sure that the deleting the mangled array fails
        self.assertEquals(array_manager.delete_array_at_index(array_idx), False)

    def test_find_array_item(self):
        """
        Tests that the starting index of an array containing a specific item
        can be found correctly
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)
        # Create an arbitrary int array
        array_size = self.TEST_BLOCK_SIZE / 4
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        array = [randint(-2**31, 2**31 - 1) for _ in range(0, rand_size + 1)]
        # Write it to the array manager
        array_manager.write_array(array, Property.PropertyType.intArray)

        # Create an arbitrary int array
        array_size = self.TEST_BLOCK_SIZE / 4
        array = array_size * [4] + [42] + array_size * [38]
        # Write it to the array manager
        search_idx1 = array_manager.write_array(array,
                                                Property.PropertyType.intArray)
        # Create an arbitrary int array
        array_size = self.TEST_BLOCK_SIZE / 4
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        array = [randint(-2**31, 2**31 - 1) for _ in range(0, rand_size + 1)]
        # Write it to the array manager
        array_manager.write_array(array, Property.PropertyType.intArray)

        # Create an arbitrary int array
        array_size = self.TEST_BLOCK_SIZE / 4
        array = array_size * [4] + [42] + array_size * [38]
        # Write it to the array manager
        search_idx2 = array_manager.write_array(array,
                                                Property.PropertyType.intArray)

        # Check that finding the item works
        self.assertEquals(array_manager.find_array_items([4, 42, 38]),
                          [search_idx1, search_idx2])

        # Check that limiting the number of found items works
        self.assertEquals(array_manager.find_array_items([4, 42, 38], 1),
                          [search_idx1])

        # Check that finding an item that does not exist works
        self.assertAlmostEqual(array_manager.find_array_items(["a"]), None)

    def test_delete_array_at_index(self):
        """
        Tests that deleting an array at a specific index works
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)
        # Create an arbitrary int array
        array_size = self.TEST_BLOCK_SIZE / 4
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        array = [randint(-2**31, 2**31 - 1) for _ in range(0, rand_size + 1)]
        # Write it to the array manager
        array_idx = array_manager.write_array(array,
                                              Property.PropertyType.intArray)
        # Check that the array is as expected
        self.assertEquals(array, array_manager.read_array_at_index(array_idx))

        # Delete the array from the array store
        array_manager.delete_array_at_index(array_idx)
        # Try to read the array, it should return None or EOF
        array = array_manager.read_array_at_index(array_idx)
        self.assertTrue(array is None or array is EOF)

    def test_delete_arrays_at_index_multiple(self):
        """
        Tests that deleting an array at a specific index works with more than
        one item in the store
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)
        # Create an arbitrary int array
        array_size = self.TEST_BLOCK_SIZE / 4
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        array1 = [randint(-2**31, 2**31 - 1) for _ in range(0, rand_size + 1)]
        # Write it to the array manager
        array_idx1 = array_manager.write_array(array1,
                                               Property.PropertyType.intArray)

        # Create a second arbitrary int array
        array_size = self.TEST_BLOCK_SIZE / 4
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        array2 = [randint(-2**31, 2**31 - 1) for _ in range(0, rand_size + 1)]
        # Write it to the array manager
        array_idx2 = array_manager.write_array(array2,
                                               Property.PropertyType.intArray)

        # Create a third arbitrary int array
        array_size = self.TEST_BLOCK_SIZE / 4
        rand_size = randint(1, 3) * array_size + randint(0, array_size - 1)
        array3 = [randint(-2**31, 2**31 - 1) for _ in range(0, rand_size + 1)]
        # Write it to the array manager
        array_idx3 = array_manager.write_array(array3,
                                               Property.PropertyType.intArray)

        # Delete the 2nd array from the array store
        array_manager.delete_array_at_index(array_idx2)
        # Try to read the array, it should return None or EOF
        array2 = array_manager.read_array_at_index(array_idx2)
        self.assertTrue(array2 is None or array2 is EOF)
        # Check that the other two are as expected
        self.assertEquals(array1, array_manager.read_array_at_index(array_idx1))
        self.assertEquals(array3, array_manager.read_array_at_index(array_idx3))

        # Delete the 1st array from the array store
        array_manager.delete_array_at_index(array_idx1)
        # Try to read the array, it should return None or EOF
        array1 = array_manager.read_array_at_index(array_idx1)
        self.assertTrue(array1 is None or array1 is EOF)
        # Check that the other two are as expected
        array2 = array_manager.read_array_at_index(array_idx2)
        self.assertTrue(array2 is None or array2 is EOF)
        self.assertEquals(array3, array_manager.read_array_at_index(array_idx3))

        # Delete the 3rd array from the array store
        array_manager.delete_array_at_index(array_idx3)
        # Try to read the array, it should return None or EOF
        array3 = array_manager.read_array_at_index(array_idx3)
        self.assertTrue(array3 is None or array3 is EOF)
        # Check that the other two are as expected
        array2 = array_manager.read_array_at_index(array_idx2)
        self.assertTrue(array2 is None or array2 is EOF)
        array1 = array_manager.read_array_at_index(array_idx1)
        self.assertTrue(array1 is None or array1 is EOF)

    def test_update_array_at_index_same_size(self):
        """
        Test that updating an array at a certain starting index works with
        same size updates.
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)
        # Create an int array spanning 1 block
        array_size = self.TEST_BLOCK_SIZE / 4
        arr1 = [randint(-2**31, 2**31 - 1) for _ in range(0, array_size)]
        # Write it to the array manager
        arr1_idx = array_manager.write_array(arr1,
                                             Property.PropertyType.intArray)
        # Check that the array is as expected
        self.assertEquals(arr1, array_manager.read_array_at_index(arr1_idx))

        # Update the array with another having the same size
        arr1_u = [randint(-2**31, 2**31 - 1) for _ in range(0, array_size)]
        array_manager.update_array_at_index(arr1_idx, arr1_u)
        self.assertEquals(arr1_u, array_manager.read_array_at_index(arr1_idx))

        # Create an int array spanning 4 blocks: 4 * (block_size / int_size)
        array_size = self.TEST_BLOCK_SIZE / 4
        arr2 = [randint(-2**31, 2**31 - 1) for _ in range(0, array_size)]
        # Write it to the array manager
        arr2_idx = array_manager.write_array(arr2,
                                             Property.PropertyType.intArray)
        # Check that the array is as expected
        self.assertEquals(arr2, array_manager.read_array_at_index(arr2_idx))

        # Update the array with another having the same size
        arr2_u = [randint(-2**31, 2**31 - 1) for _ in range(0, array_size)]
        array_manager.update_array_at_index(arr2_idx, arr2_u)
        self.assertEquals(arr2_u, array_manager.read_array_at_index(arr2_idx))

    def test_update_array_at_index_smaller_size(self):
        """
        Test that updating an array at a certain starting index works with
        smaller-size updates.
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)
        # Create a char array spanning 6 blocks: 6 * (block_size / char_size)
        array_size = 6 * (self.TEST_BLOCK_SIZE / 2)
        arr1 = [unichr(randint(0, 2**16 - 1)) for _ in range(0, array_size)]
        # Write it to the array manager
        arr1_idx = array_manager.write_array(arr1,
                                             Property.PropertyType.charArray)
        # Check that the array is as expected
        self.assertEquals(arr1, array_manager.read_array_at_index(arr1_idx))

        # Update the array with another spanning 3 blocks
        array_size = 3 * (self.TEST_BLOCK_SIZE / 2)
        arr1_u = [unichr(randint(0, 2**16 - 1)) for _ in range(0, array_size)]
        array_manager.update_array_at_index(arr1_idx, arr1_u)
        self.assertEquals(arr1_u, array_manager.read_array_at_index(arr1_idx))
        # Check residue spots are deleted (1, 2, 3 filled, indexes 4, 5, 6 left)
        self.check_residue_deletion(array_manager, arr1_idx, [3, 4, 5])

        # Create a char array spanning 2 blocks
        array_size = 2 * (self.TEST_BLOCK_SIZE / 2)
        arr2 = [unichr(randint(0, 2**16 - 1)) for _ in range(0, array_size)]
        # Write it to the array manager
        arr2_idx = array_manager.write_array(arr2,
                                             Property.PropertyType.charArray)
        # Check that the array is as expected
        self.assertEquals(arr2, array_manager.read_array_at_index(arr2_idx))

        # Update the array with another spanning 1 block
        array_size = self.TEST_BLOCK_SIZE / 2
        arr2_u = [unichr(randint(0, 2**16 - 1)) for _ in range(0, array_size)]
        array_manager.update_array_at_index(arr2_idx, arr2_u)
        self.assertEquals(arr2_u, array_manager.read_array_at_index(arr2_idx))
        # Check residue spot is deleted (1 index after the original index)
        self.check_residue_deletion(array_manager, arr2_idx, [1])

    def test_update_array_at_index_larger_size(self):
        """
        Test that updating an array at a certain starting index works with
        larger-size updates.
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)
        # Create a double array spanning 1 block: 1 * (block_size / double_size)
        array_size = self.TEST_BLOCK_SIZE / 8
        arr1 = [uniform(-10, 10) for _ in range(0, array_size)]
        # Write it to the array manager
        arr1_idx = array_manager.write_array(arr1,
                                             Property.PropertyType.doubleArray)
        # Check that the array is as expected
        self.assertEquals(arr1, array_manager.read_array_at_index(arr1_idx))

        # Update the array with another spanning 5 blocks
        array_size = 5 * (self.TEST_BLOCK_SIZE / 8)
        arr1_u = [uniform(-10, 10) for _ in range(0, array_size)]
        array_manager.update_array_at_index(arr1_idx, arr1_u)
        self.assertEquals(arr1_u, array_manager.read_array_at_index(arr1_idx))

        # Create a double array spanning 4 blocks
        array_size = 4 * (self.TEST_BLOCK_SIZE / 8)
        arr2 = [uniform(-10, 10) for _ in range(0, array_size)]
        # Write it to the array manager
        arr2_idx = array_manager.write_array(arr2,
                                             Property.PropertyType.doubleArray)
        # Check that the array is as expected
        self.assertEquals(arr2, array_manager.read_array_at_index(arr2_idx))

        # Update the array with another spanning 7 blocks
        array_size = 7 * (self.TEST_BLOCK_SIZE / 8)
        arr2_u = [uniform(-10, 10) for _ in range(0, array_size)]
        array_manager.update_array_at_index(arr2_idx, arr2_u)
        self.assertEquals(arr2_u, array_manager.read_array_at_index(arr2_idx))

    def test_update_string_array_same_size(self):
        """
        Test that updating a string array at a certain starting index works
        with same-size updates.
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)
        # Create a string array spanning 1 block: 1 * (block_size / string_size)
        arr_size = self.TEST_BLOCK_SIZE / 4 - 4
        # With strings that span 3 blocks
        string_size = 3 * self.TEST_STRING_BLOCK_SIZE
        arr1 = [string_size * "A" for _ in range(0, arr_size)]
        arr1_idx = array_manager.write_array(arr1,
                                             Property.PropertyType.stringArray)
        # Check that the array is as expected
        self.assertEquals(arr1, array_manager.read_array_at_index(arr1_idx))

        # Update the array with another having the same size
        arr1_u = [string_size * "B" for _ in range(0, arr_size)]
        array_manager.update_array_at_index(arr1_idx, arr1_u)
        self.assertEquals(arr1_u, array_manager.read_array_at_index(arr1_idx))

        # Create a string array spanning 3 blocks
        arr_size = 2 * (self.TEST_BLOCK_SIZE / 4) + 2
        # With strings that span 2 blocks
        string_size = 2 * self.TEST_STRING_BLOCK_SIZE
        arr2 = [string_size * "C" for _ in range(0, arr_size)]
        arr2_idx = array_manager.write_array(arr2,
                                             Property.PropertyType.stringArray)
        # Check that the array is as expected
        self.assertEquals(arr2, array_manager.read_array_at_index(arr2_idx))

        # Update the array with another having the same size
        arr2_u = [string_size * "D" for _ in range(0, arr_size)]
        array_manager.update_array_at_index(arr2_idx, arr2_u)
        self.assertEquals(arr2_u, array_manager.read_array_at_index(arr2_idx))

        # Create a string array spanning 1 block
        arr_size = self.TEST_BLOCK_SIZE / 4
        # With strings that span 2 blocks
        string_size = 2 * self.TEST_STRING_BLOCK_SIZE
        arr3 = [string_size * "E" for _ in range(0, arr_size)]
        arr3_idx = array_manager.write_array(arr3,
                                             Property.PropertyType.stringArray)
        # Check that the array is as expected
        self.assertEquals(arr3, array_manager.read_array_at_index(arr3_idx))

        # Update array with another having the same size, increase string size
        string_size = 4 * self.TEST_STRING_BLOCK_SIZE
        arr3_u = [string_size * "F" for _ in range(0, arr_size)]
        array_manager.update_array_at_index(arr3_idx, arr3_u)
        self.assertEquals(arr3_u, array_manager.read_array_at_index(arr3_idx))

        # Update array with another having the same size, decrease string size
        string_size = self.TEST_STRING_BLOCK_SIZE
        arr3_u = [string_size * "G" for _ in range(0, arr_size)]
        array_manager.update_array_at_index(arr3_idx, arr3_u)
        self.assertEquals(arr3_u, array_manager.read_array_at_index(arr3_idx))

    def test_update_string_array_smaller_size(self):
        """
        Test that updating a string array at a certain starting index works
        with smaller-size updates.
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)
        # Create a string array spanning 5 blocks: 5 * (block_size / str_size)
        arr_size = 5 * (self.TEST_BLOCK_SIZE / 4) - 3
        # With strings that span 3 blocks
        string_size = 3 * self.TEST_STRING_BLOCK_SIZE
        arr1 = [string_size * "A" for _ in range(0, arr_size)]
        arr1_idx = array_manager.write_array(arr1,
                                             Property.PropertyType.stringArray)
        # Check that the array is as expected
        self.assertEquals(arr1, array_manager.read_array_at_index(arr1_idx))
        # Update the array with another spanning 1 block
        # Tests case (1) of update_names_at_indexes since our only block will
        # need 1 less string ID than the first block before the update provides
        arr_size = self.TEST_BLOCK_SIZE / 4 - 1
        arr1_u = [string_size * "B" for _ in range(0, arr_size)]
        array_manager.update_array_at_index(arr1_idx, arr1_u)
        self.assertEquals(arr1_u, array_manager.read_array_at_index(arr1_idx))
        # Check residue blocks are deleted, assume strings are deleted
        self.check_residue_deletion(array_manager, arr1_idx, [1, 2, 3, 4])

        # Create a string array spanning 3 blocks
        arr_size = 3 * (self.TEST_BLOCK_SIZE / 4) + 5
        # With strings that span 2 blocks
        string_size = 2 * self.TEST_STRING_BLOCK_SIZE
        arr2 = [string_size * "C" for _ in range(0, arr_size)]
        arr2_idx = array_manager.write_array(arr2,
                                             Property.PropertyType.stringArray)
        # Check that the array is as expected
        self.assertEquals(arr2, array_manager.read_array_at_index(arr2_idx))

        # Update the array with another spanning 2 blocks
        arr_size = self.TEST_BLOCK_SIZE / 4 + 1
        arr2_u = [string_size * "D" for _ in range(0, arr_size)]
        array_manager.update_array_at_index(arr2_idx, arr2_u)
        self.assertEquals(arr2_u, array_manager.read_array_at_index(arr2_idx))
        # Check residue block is deleted, assume strings are deleted
        self.check_residue_deletion(array_manager, arr2_idx, [2])

        # Create a string array spanning 3 blocks
        arr_size = 2 * (self.TEST_BLOCK_SIZE / 4) + 2
        # With strings that span 2 blocks
        string_size = 2 * self.TEST_STRING_BLOCK_SIZE
        arr3 = [string_size * "E" for _ in range(0, arr_size)]
        arr3_idx = array_manager.write_array(arr3,
                                             Property.PropertyType.stringArray)
        # Check that the array is as expected
        self.assertEquals(arr3, array_manager.read_array_at_index(arr3_idx))

        # Update array with another spanning 2 blocks, increase string size
        arr_size = self.TEST_BLOCK_SIZE / 4 + 1
        string_size = 4 * self.TEST_STRING_BLOCK_SIZE
        arr3_u = [string_size * "F" for _ in range(0, arr_size)]
        array_manager.update_array_at_index(arr3_idx, arr3_u)
        self.assertEquals(arr3_u, array_manager.read_array_at_index(arr3_idx))
        # Check residue block is deleted, assume strings are deleted
        self.check_residue_deletion(array_manager, arr3_idx, [2])

        # Update array with another spanning 1 block, decrease string size
        arr_size = self.TEST_BLOCK_SIZE / 4
        string_size = self.TEST_STRING_BLOCK_SIZE
        arr3_u = [string_size * "G" for _ in range(0, arr_size)]
        array_manager.update_array_at_index(arr3_idx, arr3_u)
        self.assertEquals(arr3_u, array_manager.read_array_at_index(arr3_idx))
        # Check residue block is deleted, assume strings are deleted
        self.check_residue_deletion(array_manager, arr3_idx, [1])

    def test_update_string_array_larger_size(self):
        """
        Test that updating a string array at a certain starting index works
        with larger-size updates.
        """
        array_manager = GeneralArrayManager(self.TEST_BLOCK_SIZE,
                                            self.TEST_STRING_BLOCK_SIZE)
        # Create a string array spanning 1 block: 1 * (block_size / string_size)
        arr_size = self.TEST_BLOCK_SIZE / 4 - 3
        # With strings that span 3 blocks
        string_size = 3 * self.TEST_STRING_BLOCK_SIZE
        arr1 = [string_size * "A" for _ in range(0, arr_size)]
        arr1_idx = array_manager.write_array(arr1,
                                             Property.PropertyType.stringArray)
        # Check that the array is as expected
        self.assertEquals(arr1, array_manager.read_array_at_index(arr1_idx))

        # Update the array with another spanning 5 blocks
        # Tests case (2) of update_names_at_indexes since our last block will
        # need 3 more string IDs than the last block before the update provides
        arr_size = 5 * (self.TEST_BLOCK_SIZE / 4)
        arr1_u = [string_size * "B" for _ in range(0, arr_size)]
        array_manager.update_array_at_index(arr1_idx, arr1_u)
        self.assertEquals(arr1_u, array_manager.read_array_at_index(arr1_idx))

        # Create a string array spanning 3 blocks
        arr_size = 3 * (self.TEST_BLOCK_SIZE / 4)
        # With strings that span 2 blocks
        string_size = 2 * self.TEST_STRING_BLOCK_SIZE
        arr2 = [string_size * "C" for _ in range(0, arr_size)]
        arr2_idx = array_manager.write_array(arr2,
                                             Property.PropertyType.stringArray)
        # Check that the array is as expected
        self.assertEquals(arr2, array_manager.read_array_at_index(arr2_idx))

        # Update the array with another spanning 6 blocks
        arr_size = 6 * (self.TEST_BLOCK_SIZE / 4)
        arr2_u = [string_size * "D" for _ in range(0, arr_size)]
        array_manager.update_array_at_index(arr2_idx, arr2_u)
        self.assertEquals(arr2_u, array_manager.read_array_at_index(arr2_idx))

        # Create a string array spanning 1 block
        arr_size = self.TEST_BLOCK_SIZE / 4
        # With strings that span 2 blocks
        string_size = 2 * self.TEST_STRING_BLOCK_SIZE
        arr3 = [string_size * "E" for _ in range(0, arr_size)]
        arr3_idx = array_manager.write_array(arr3,
                                             Property.PropertyType.stringArray)
        # Check that the array is as expected
        self.assertEquals(arr3, array_manager.read_array_at_index(arr3_idx))

        # Update array with another spanning 3 blocks, increase string size
        arr_size = 3 * (self.TEST_BLOCK_SIZE / 4)
        string_size = 4 * self.TEST_STRING_BLOCK_SIZE
        arr3_u = [string_size * "F" for _ in range(0, arr_size)]
        array_manager.update_array_at_index(arr3_idx, arr3_u)
        self.assertEquals(arr3_u, array_manager.read_array_at_index(arr3_idx))

        # Update array with another spanning 4 blocks, decrease string size
        arr_size = 4 * (self.TEST_BLOCK_SIZE / 4)
        string_size = self.TEST_STRING_BLOCK_SIZE
        arr3_u = [string_size * "G" for _ in range(0, arr_size)]
        array_manager.update_array_at_index(arr3_idx, arr3_u)
        self.assertEquals(arr3_u, array_manager.read_array_at_index(arr3_idx))

    def check_residue_deletion(self, array_manager, start, residue_indexes):
        """
        Check that the given residue spots from smaller updates are deleted.
        Indexes checked will be at start + residue_indexes[i]
        """
        for i in residue_indexes:
            old_item = array_manager.storeManager.get_item_at_index(start + i)
            self.assertTrue(old_item is None or old_item is EOF)