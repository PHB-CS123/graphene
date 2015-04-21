import unittest

from graphene.storage.base.general_type_store import *


class TestGeneralTypeStoreMethods(unittest.TestCase):
    TEST_FILENAME = "graphenestore.generaltypestore.db"
    
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
        Test that initializing an empty GeneralTypeStore succeeds
        (file is opened)
        """
        try:
            GeneralTypeStore(self.TEST_FILENAME)
        except IOError:
            self.fail("GeneralTypeStore initializer failed: "
                      "db file failed to open.")

    def test_double_init(self):
        """
        Test that initializing an empty GeneralTypeStore succeeds when
        repeated; i.e. the old file is reopened and no errors occur.
        """
        try:
            GeneralTypeStore(self.TEST_FILENAME)
        except IOError:
            self.fail("GeneralTypeStore initializer failed: "
                      "db file failed to open.")
        try:
            GeneralTypeStore(self.TEST_FILENAME)
        except IOError:
            self.fail("GeneralTypeStore initializer failed on second attempt: "
                      "db file failed to open.")

    def test_invalid_write(self):
        """
        Test that writing a type to index 0 raises an error
        """
        type_store = GeneralTypeStore(self.TEST_FILENAME)

        empty_type = GeneralType()
        with self.assertRaises(ValueError):
            type_store.write_item(empty_type)

    def test_invalid_read(self):
        """
        Test that reading a type from index 0 raises an error
        """
        type_store = GeneralTypeStore(self.TEST_FILENAME)

        with self.assertRaises(ValueError):
            type_store.item_at_index(0)

    def test_empty_read(self):
        """
        Make sure that reading an item when the file is empty returns None
        """
        type_store = GeneralTypeStore(self.TEST_FILENAME)
        # Read an uncreated item
        no_item = type_store.item_at_index(1)
        # Make sure it returned None
        self.assertEquals(no_item, None)

    def test_write_read_1_type(self):
        """
        Tests that the type_value written to the GeneralTypeStore is
        the type_value that is read.
        """
        type_store = GeneralTypeStore(self.TEST_FILENAME)

        # Create a type_value and add it to the GeneralTypeStore
        type_value = GeneralType(1, False, 1, 1)
        type_store.write_item(type_value)

        # Read the type_value from the GeneralTypeStore file
        type_file = type_store.item_at_index(type_value.index)

        # Assert that the values are the same
        self.assertEquals(type_value, type_file)

    def test_write_read_2_types(self):
        """
        Tests when 2 types are written after 1 type to the GeneralTypeStore
        """
        type_store = GeneralTypeStore(self.TEST_FILENAME)

        # Create one type and write it to the GeneralTypeStore
        type1 = GeneralType(1, False, 1, 1)
        type_store.write_item(type1)

        # Create 2 types and add them to the GeneralTypeStore
        type2 = GeneralType(2, False, 2, 2)
        type3 = GeneralType(3, False, 3, 3)
        type_store.write_item(type2)
        type_store.write_item(type3)

        # Read the types from the GeneralTypeStore file
        type1_file = type_store.item_at_index(type1.index)
        type2_file = type_store.item_at_index(type2.index)
        type3_file = type_store.item_at_index(type3.index)

        # Make sure their values are the same
        self.assertEquals(type1, type1_file)
        self.assertEquals(type2, type2_file)
        self.assertEquals(type3, type3_file)

    def test_overwrite_type(self):
        """
        Tests that overwriting a type in a database with 3 types works
        """
        type_store = GeneralTypeStore(self.TEST_FILENAME)

        # Create 3 types
        type1 = GeneralType(1, False, 1, 1)
        type2 = GeneralType(2, False, 2, 2)
        type3 = GeneralType(3, False, 3, 3)

        # Write them to the type store
        type_store.write_item(type1)
        type_store.write_item(type2)
        type_store.write_item(type3)

        # Verify that they are in the store as expected
        type1_file = type_store.item_at_index(type1.index)
        self.assertEquals(type1, type1_file)

        type2_file = type_store.item_at_index(type2.index)
        self.assertEquals(type2, type2_file)

        type3_file = type_store.item_at_index(type3.index)
        self.assertEquals(type3, type3_file)

        # Create a new type2 and overwrite the old type2
        new_type2 = GeneralType(2, True, 8, 8)
        type_store.write_item(new_type2)

        # Verify that the data is still as expected
        type1_file = type_store.item_at_index(type1.index)
        self.assertEquals(type1, type1_file)

        new_type2_file = type_store.item_at_index(new_type2.index)
        self.assertEquals(new_type2, new_type2_file)

        type3_file = type_store.item_at_index(type3.index)
        self.assertEquals(type3, type3_file)

    def test_delete_type(self):
        """
        Tests that deleting 2 types in a database with 3 types works
        """
        type_store = GeneralTypeStore(self.TEST_FILENAME)

        # Create 3 types
        type1 = GeneralType(1, True, 1, 1)
        type2 = GeneralType(2, True, 2, 2)
        type3 = GeneralType(3, True, 3, 3)

        # Write them to the type store
        type_store.write_item(type1)
        type_store.write_item(type2)
        type_store.write_item(type3)

        # Verify that they are in the store as expected
        type1_file = type_store.item_at_index(type1.index)
        self.assertEquals(type1, type1_file)

        type2_file = type_store.item_at_index(type2.index)
        self.assertEquals(type2, type2_file)

        type3_file = type_store.item_at_index(type3.index)
        self.assertEquals(type3, type3_file)

        # Delete types 1 and 3
        type_store.delete_item(type1)
        type_store.delete_item(type3)

        # Verify deleted type is deleted
        deleted_type1_file = type_store.item_at_index(type1.index)
        self.assertEquals(deleted_type1_file, None)

        # Verify unaffected type is as expected
        type2_file = type_store.item_at_index(type2.index)
        self.assertEquals(type2, type2_file)

        # Verify deleted type is deleted
        deleted_type3_file = type_store.item_at_index(type3.index)
        self.assertEquals(deleted_type3_file, None)
