import unittest

from graphene.storage.base.general_type_type_store import *


class TestGeneralTypeTypeStoreMethods(unittest.TestCase):
    TEST_FILENAME = "graphenestore.generaltypetypestore.db"

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
        Test that initializing an empty GeneralTypeTypeStore succeeds
        (file is opened)
        """
        try:
            GeneralTypeTypeStore(self.TEST_FILENAME)
        except IOError:
            self.fail("GeneralTypeStore initializer failed: "
                      "db file failed to open.")

    def test_double_init(self):
        """
        Test that initializing an empty GeneralTypeTypeStore succeeds when
        repeated; i.e. the old file is reopened and no errors occur.
        """
        try:
            GeneralTypeTypeStore(self.TEST_FILENAME)
        except IOError:
            self.fail("GeneralTypeStore initializer failed: "
                      "db file failed to open.")
        try:
            GeneralTypeTypeStore(self.TEST_FILENAME)
        except IOError:
            self.fail("GeneralTypeStore initializer failed on second attempt: "
                      "db file failed to open.")

    def test_invalid_write(self):
        """
        Test that writing a type of a type to index 0 raises an error
        """
        type_type_store = GeneralTypeTypeStore(self.TEST_FILENAME)

        empty_type = GeneralTypeType()
        with self.assertRaises(ValueError):
            type_type_store.write_item(empty_type)

    def test_invalid_read(self):
        """
        Test that reading a type of a type from index 0 raises an error
        """
        type_type_store = GeneralTypeTypeStore(self.TEST_FILENAME)

        with self.assertRaises(ValueError):
            type_type_store.item_at_index(0)

    def test_empty_read(self):
        """
        Make sure that reading an item when the file is empty returns None
        """
        type_type_store = GeneralTypeTypeStore(self.TEST_FILENAME)
        # Read an uncreated item
        no_item = type_type_store.item_at_index(1)
        # Make sure it returned None
        self.assertEquals(no_item, GeneralStore.EOF)

    def test_write_read_1_type(self):
        """
        Tests that the type of a type written to the GeneralTypeTypeStore
        is the type of type that is read.
        """
        type_type_store = GeneralTypeTypeStore(self.TEST_FILENAME)

        # Create a type of a type and add it to the GeneralTypeTypeStore
        type_t = GeneralTypeType(1, False, 1, Property.PropertyType.int, 1)
        type_type_store.write_item(type_t)

        # Read the type of a type from the GeneralTypeTypeStore file
        type_t_file = type_type_store.item_at_index(type_t.index)

        # Assert that the values are the same
        self.assertEquals(type_t, type_t_file)

    def test_write_read_2_types(self):
        """
        Tests when 2 types of types are written after 1 type of a type
        to the GeneralTypeTypeStore
        """
        type_type_store = GeneralTypeTypeStore(self.TEST_FILENAME)

        # Create one type of a type and write it to the GeneralTypeTypeStore
        type_t1 = GeneralTypeType(1, False, 1, Property.PropertyType.long, 1)
        type_type_store.write_item(type_t1)

        # Create 2 types of a type and add them to the GeneralTypeTypeStore
        type_t2 = GeneralTypeType(2, False, 2, Property.PropertyType.float, 2)
        type_t3 = GeneralTypeType(3, False, 3, Property.PropertyType.string, 3)
        type_type_store.write_item(type_t2)
        type_type_store.write_item(type_t3)

        # Read the types of types from the GeneralTypeTypeStore file
        type_t1_file = type_type_store.item_at_index(type_t1.index)
        type_t2_file = type_type_store.item_at_index(type_t2.index)
        type_t3_file = type_type_store.item_at_index(type_t3.index)

        # Make sure their values are the same
        self.assertEquals(type_t1, type_t1_file)
        self.assertEquals(type_t2, type_t2_file)
        self.assertEquals(type_t3, type_t3_file)

    def test_overwrite_type(self):
        """
        Tests that overwriting a type of a type in a database with 3 types
        of types works
        """
        type_type_store = GeneralTypeTypeStore(self.TEST_FILENAME)

        # Create 3 types of types
        type_t1 = GeneralTypeType(1, True, 1, Property.PropertyType.intArray, 1)
        type_t2 = GeneralTypeType(2, False, 2, Property.PropertyType.bool, 2)
        type_t3 = GeneralTypeType(3, False, 3, Property.PropertyType.double, 3)

        # Write them to the type of types store
        type_type_store.write_item(type_t1)
        type_type_store.write_item(type_t2)
        type_type_store.write_item(type_t3)

        # Verify that they are in the store as expected
        type_t1_file = type_type_store.item_at_index(type_t1.index)
        self.assertEquals(type_t1, type_t1_file)

        type_t2_file = type_type_store.item_at_index(type_t2.index)
        self.assertEquals(type_t2, type_t2_file)

        type_t3_file = type_type_store.item_at_index(type_t3.index)
        self.assertEquals(type_t3, type_t3_file)

        # Create a new type_t2 and overwrite the old type_t2
        new_type_t2 = GeneralTypeType(2, True, 8, Property.PropertyType.int, 8)
        type_type_store.write_item(new_type_t2)

        # Verify that the data is still as expected
        type_t1_file = type_type_store.item_at_index(type_t1.index)
        self.assertEquals(type_t1, type_t1_file)

        new_type_t2_file = type_type_store.item_at_index(new_type_t2.index)
        self.assertEquals(new_type_t2, new_type_t2_file)

        type_t3_file = type_type_store.item_at_index(type_t3.index)
        self.assertEquals(type_t3, type_t3_file)

    def test_delete_type(self):
        """
        Tests that deleting 2 types of types in a database with 3
        types of types works
        """
        type_type_store = GeneralTypeTypeStore(self.TEST_FILENAME)

        # Create 3 types of types
        type_t1 = GeneralTypeType(1, True, 1, Property.PropertyType.short, 1)
        type_t2 = GeneralTypeType(2, True, 2,
                                  Property.PropertyType.doubleArray, 2)
        type_t3 = GeneralTypeType(3, True, 3,
                                  Property.PropertyType.stringArray, 3)

        # Write them to the type of types store
        type_type_store.write_item(type_t1)
        type_type_store.write_item(type_t2)
        type_type_store.write_item(type_t3)

        # Verify that they are in the store as expected
        type_t1_file = type_type_store.item_at_index(type_t1.index)
        self.assertEquals(type_t1, type_t1_file)

        type_t2_file = type_type_store.item_at_index(type_t2.index)
        self.assertEquals(type_t2, type_t2_file)

        type_t3_file = type_type_store.item_at_index(type_t3.index)
        self.assertEquals(type_t3, type_t3_file)

        # Delete types of types 1 and 3
        type_type_store.delete_item(type_t1)
        # Deleting from end of file, should return EOF when read
        type_type_store.delete_item(type_t3)

        # Verify deleted type of type is deleted
        deleted_type_t1_file = type_type_store.item_at_index(type_t1.index)
        self.assertIsNone(deleted_type_t1_file)

        # Verify unaffected type of type is as expected
        type_t2_file = type_type_store.item_at_index(type_t2.index)
        self.assertEquals(type_t2, type_t2_file)

        # Verify deleted type of type is deleted
        deleted_type3_file = type_type_store.item_at_index(type_t3.index)
        self.assertEquals(deleted_type3_file, EOF)
