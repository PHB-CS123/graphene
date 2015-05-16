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
        with self.assertRaises(EOFError):
            array_manager.read_array_at_index(1)

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
        Test that when reading a mangled array, the method returns None
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

        # Mangle the array by deleting from the second block (first block intact)
        array_manager.storeManager.delete_item_at_index(array_idx + 1)

        # Make sure that the read_name_at_index method returns None
        self.assertEquals(array_manager.read_array_at_index(array_idx), None)

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
        # Make sure that the read_name_at_index method returns None
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
        # Try to read the array, it should return None
        self.assertEquals(array_manager.read_array_at_index(array_idx), None)

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
        # Try to read the array, it should return None
        self.assertEquals(array_manager.read_array_at_index(array_idx2), None)
        # Check that the other two are as expected
        self.assertEquals(array1, array_manager.read_array_at_index(array_idx1))
        self.assertEquals(array3, array_manager.read_array_at_index(array_idx3))

        # Delete the 1st array from the array store
        array_manager.delete_array_at_index(array_idx1)
        # Try to read the array, it should return None
        self.assertEquals(array_manager.read_array_at_index(array_idx1), None)
        # Check that the other two are as expected
        self.assertEquals(array_manager.read_array_at_index(array_idx2), None)
        self.assertEquals(array3, array_manager.read_array_at_index(array_idx3))

        # Delete the 3rd array from the array store
        array_manager.delete_array_at_index(array_idx3)
        # Try to read the array, it should return None
        self.assertEquals(array_manager.read_array_at_index(array_idx3), None)
        # Check that the other two are as expected
        self.assertEquals(array_manager.read_array_at_index(array_idx2), None)
        self.assertEquals(array_manager.read_array_at_index(array_idx1), None)
