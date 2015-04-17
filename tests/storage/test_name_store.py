import unittest

from graphene.storage.name_store import *


class TestNameStoreMethods(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_empty_init(self):
        """
        Test that initializing an empty NameStore succeeds (file is opened)
        """
        try:
            NameStore("graphenestore.namestore.db")
        except IOError:
            self.fail("NameStore initializer failed: db file failed to open.")

    def test_double_init(self):
        """
        Test that initializing an empty NameStore succeeds when
        repeated; i.e. the old file is reopened and no errors occur.
        """
        try:
            NameStore("graphenestore.namestore.db")
        except IOError:
            self.fail("NameStore initializer failed: "
                      "db file failed to open.")
        try:
            NameStore("graphenestore.namestore.db")
        except IOError:
            self.fail("NameStore initializer failed on second attempt: "
                      "db file failed to open.")

    def test_invalid_write(self):
        """
        Test that writing a name to index 0 raises an error
        """
        name_store = NameStore("graphenestore.namestore.db")

        empty_name = Name()
        with self.assertRaises(ValueError):
            name_store.write_item(empty_name)

    def test_invalid_read(self):
        """
        Test that reading a name from index 0 raises an error
        """
        name_store = NameStore("graphenestore.namestore.db")

        with self.assertRaises(ValueError):
            name_store.item_at_index(0)

    def test_invalid_length_write(self):
        """
        Test that writing a string with length longer than blockSize
        raises an error
        """
        block_size = 20
        name_store = NameStore("graphenestore.namestore.db", block_size)

        # Try to write a name that is 1 byte longer than the largest block_size
        long_name = Name(1, True, 0, 1, 0, (block_size + 1) * "a")
        with self.assertRaises(ValueError):
            name_store.write_item(long_name)

    def test_write_read_1_name(self):
        """
        Tests that the name written to the NameStore is the name that is read.
        """
        name_store = NameStore("graphenestore.namestore.db")

        # Create a name and add it to the NameStore
        name_data = Name(1, True, 0, 1, 0, "hello")
        name_store.write_item(name_data)

        # Read the name from the NameStore file
        name_data_file = name_store.item_at_index(name_data.index)

        # Assert that the values are the same
        self.assertEquals(name_data, name_data_file)

    def test_write_read_2_names(self):
        """
        Tests when 2 names are written after 1 name to the NameStore
        """
        name_store = NameStore("graphenestore.namestore.db")

        # Create one name and write it to the NameStore
        name_data1 = Name(1, True, 0, 1, 0, "hello")
        name_store.write_item(name_data1)

        # Create 2 names and add them to the NameStore
        name_data2 = Name(2, True, 2, 1, 2, "bye")
        name_data3 = Name(3, False, 3, 1, 3, "bye bye")
        name_store.write_item(name_data2)
        name_store.write_item(name_data3)

        # Read the names from the NameStore file
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
        name_store = NameStore("graphenestore.namestore.db")

        # Create 3 names
        name_data1 = Name(1, True, 0, 1, 0, "hello")
        name_data2 = Name(2, True, 2, 1, 2, "bye")
        name_data3 = Name(3, False, 3, 1, 3, "bye bye")

        # Write them to the NameStore
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
        new_name_data2 = Name(2, False, 4, 1, 4, "never mind")
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
        name_store = NameStore("graphenestore.namestore.db")

        # Create 3 names
        name_data1 = Name(1, True, 0, 1, 0, "hello")
        name_data2 = Name(2, True, 2, 1, 2, "bye")
        name_data3 = Name(3, False, 3, 1, 3, "bye bye")

        # Write them to the NameStore
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

        # Create names 1 and 3 with zeroed out values
        zero_name_data1 = Name(name_data1.index, False, 0, 0, 0, '')
        zero_name_data3 = Name(name_data3.index, False, 0, 0, 0, '')

        # Verify deleted name is zeroed out
        deleted_name_data1_file = name_store.item_at_index(name_data1.index)
        self.assertEquals(zero_name_data1, deleted_name_data1_file)

        # Verify unaffected name is as expected
        name_data2_file = name_store.item_at_index(name_data2.index)
        self.assertEquals(name_data2, name_data2_file)

        # Verify deleted name is zeroed out
        deleted_name_data3_file = name_store.item_at_index(name_data3.index)
        self.assertEquals(zero_name_data3, deleted_name_data3_file)

