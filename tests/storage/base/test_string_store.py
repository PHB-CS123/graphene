import unittest

from graphene.storage.base.string_store import *


class TestNameStoreMethods(unittest.TestCase):
    TEST_FILENAME = "graphenestore.namestore.db"

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
        Test that initializing a StringStore succeeds (file is opened)
        """
        try:
            StringStore(self.TEST_FILENAME)
        except IOError:
            self.fail("StringStore initializer failed: db file failed to open.")

    def test_double_init(self):
        """
        Test that initializing a StringStore succeeds when repeated;
        i.e. the old file is reopened and no errors occur.
        """
        try:
            StringStore(self.TEST_FILENAME)
        except IOError:
            self.fail("StringStore initializer failed: "
                      "db file failed to open.")
        try:
            StringStore(self.TEST_FILENAME)
        except IOError:
            self.fail("StringStore initializer failed on second attempt: "
                      "db file failed to open.")

    def test_invalid_write(self):
        """
        Test that writing a name to index 0 raises an error
        """
        name_store = StringStore(self.TEST_FILENAME)

        empty_name = String()
        with self.assertRaises(ValueError):
            name_store.write_item(empty_name)

    def test_invalid_read(self):
        """
        Test that reading a name from index 0 raises an error
        """
        name_store = StringStore(self.TEST_FILENAME)

        with self.assertRaises(ValueError):
            name_store.item_at_index(0)

    def test_empty_read(self):
        """
        Make sure that reading an item when the file is empty returns None
        """
        name_store = StringStore(self.TEST_FILENAME)
        # Read an uncreated item
        no_item = name_store.item_at_index(1)
        # Make sure it returned None
        self.assertEquals(no_item, GeneralStore.EOF)

    def test_invalid_length_write(self):
        """
        Test that writing a string with length longer than blockSize
        raises an error
        """
        block_size = 20
        name_store = StringStore(self.TEST_FILENAME, block_size)

        # Try to write a name that is 1 byte longer than the largest block_size
        long_name = String(1, True, 0, 1, 0, (block_size + 1) * "a")
        with self.assertRaises(ValueError):
            name_store.write_item(long_name)

    def test_write_read_1_name(self):
        """
        Tests that the name written to the StringStore is the name that is read.
        """
        name_store = StringStore(self.TEST_FILENAME)

        # Create a name and add it to the StringStore
        name_data = String(1, True, 0, 1, 0, "hello")
        name_store.write_item(name_data)

        # Read the name from the StringStore file
        name_data_file = name_store.item_at_index(name_data.index)

        # Assert that the values are the same
        self.assertEquals(name_data, name_data_file)

    def test_write_read_2_names(self):
        """
        Tests when 2 names are written after 1 name to the StringStore
        """
        name_store = StringStore(self.TEST_FILENAME)

        # Create one name and write it to the StringStore
        name_data1 = String(1, True, 0, 1, 0, "hello")
        name_store.write_item(name_data1)

        # Create 2 names and add them to the StringStore
        name_data2 = String(2, True, 2, 1, 2, "bye")
        name_data3 = String(3, False, 3, 1, 3, "bye bye")
        name_store.write_item(name_data2)
        name_store.write_item(name_data3)

        # Read the names from the StringStore file
        name_data1_file = name_store.item_at_index(name_data1.index)
        name_data2 = name_store.item_at_index(name_data2.index)
        name_data3 = name_store.item_at_index(name_data3.index)

        # Make sure their values are the same
        self.assertEquals(name_data1, name_data1_file)
        self.assertEquals(name_data2, name_data2)
        self.assertEquals(name_data3, name_data3)

    def test_overwrite_name(self):
        """
        Tests that overwriting a name in a database with 3 names works
        """
        name_store = StringStore(self.TEST_FILENAME)

        # Create 3 names
        name_data1 = String(1, True, 0, 1, 0, "hello")
        name_data2 = String(2, True, 2, 1, 2, "bye")
        name_data3 = String(3, False, 3, 1, 3, "bye bye")

        # Write them to the StringStore
        name_store.write_item(name_data1)
        name_store.write_item(name_data2)
        name_store.write_item(name_data3)

        # Verify that they are in the store as expected
        name_data1_file = name_store.item_at_index(name_data1.index)
        self.assertEquals(name_data1, name_data1_file)

        name_data2_file = name_store.item_at_index(name_data2.index)
        self.assertEquals(name_data2, name_data2_file)

        name_data3_file = name_store.item_at_index(name_data3.index)
        self.assertEquals(name_data3, name_data3_file)

        # Create a new name_data2 and overwrite the old name_data2
        new_name_data2 = String(2, False, 4, 1, 4, "never mind")
        name_store.write_item(new_name_data2)

        # Verify that the data is still as expected
        name_data1_file = name_store.item_at_index(name_data1.index)
        self.assertEquals(name_data1, name_data1_file)

        new_name_data2_file = name_store.item_at_index(new_name_data2.index)
        self.assertEquals(new_name_data2, new_name_data2_file)

        name_data3_file = name_store.item_at_index(name_data3.index)
        self.assertEquals(name_data3, name_data3_file)

    def test_delete_name(self):
        """
        Tests that deleting 2 names in a database with 3 names works
        """
        name_store = StringStore(self.TEST_FILENAME)

        # Create 3 names
        name_data1 = String(1, True, 0, 1, 0, "hello")
        name_data2 = String(2, True, 2, 1, 2, "bye")
        name_data3 = String(3, False, 3, 1, 3, "bye bye")

        # Write them to the StringStore
        name_store.write_item(name_data1)
        name_store.write_item(name_data2)
        name_store.write_item(name_data3)

        # Verify that they are in the store as expected
        name_data1_file = name_store.item_at_index(name_data1.index)
        self.assertEquals(name_data1, name_data1_file)

        name_data2_file = name_store.item_at_index(name_data2.index)
        self.assertEquals(name_data2, name_data2_file)

        name_data3_file = name_store.item_at_index(name_data3.index)
        self.assertEquals(name_data3, name_data3_file)

        # Delete names 1 and 3
        name_store.delete_item(name_data1)
        name_store.delete_item(name_data3)

        # Verify deleted name is deleted
        deleted_name_data1_file = name_store.item_at_index(name_data1.index)
        self.assertIsNone(deleted_name_data1_file)

        # Verify unaffected name is as expected
        name_data2_file = name_store.item_at_index(name_data2.index)
        self.assertEquals(name_data2, name_data2_file)

        # Verify deleted name is deleted
        deleted_name_data3_file = name_store.item_at_index(name_data3.index)
        self.assertEquals(deleted_name_data3_file, EOF)

