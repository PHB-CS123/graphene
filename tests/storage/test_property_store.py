import unittest

from graphene.storage.property_store import *


class TestPropertyStoreMethods(unittest.TestCase):
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
        Test that initializing an empty PropertyStore succeeds
        (file is opened successfully)
        """
        try:
            PropertyStore()
        except IOError:
            self.fail("PropertyStore initializer failed: "
                      "db file failed to open.")

    def test_double_init(self):
        """
        Test that initializing an empty PropertyStore succeeds when
        repeated; i.e. the old file is reopened and no errors occur.
        """
        try:
            PropertyStore()
        except IOError:
            self.fail("PropertyStore initializer failed: "
                      "db file failed to open.")
        try:
            PropertyStore()
        except IOError:
            self.fail("PropertyStore initializer failed on second attempt: "
                      "db file failed to open.")

    def test_invalid_write(self):
        """
        Test that writing a property to offset 0 raises an error
        """
        property_store = PropertyStore()

        empty_property = Property()
        with self.assertRaises(ValueError):
            property_store.write_item(empty_property)

    def test_invalid_read(self):
        """
        Test that reading a property from offset 0 raises an error
        """
        property_store = PropertyStore()

        with self.assertRaises(ValueError):
            property_store.item_at_index(0)

    def test_write_read_1_property(self):
        """
        Tests that the property written to the PropertyStore is the
        property that is read.
        """
        property_store = PropertyStore()

        # Create a property and add it to the PropertyStore file
        db_property = Property(1, False, Property.PropertyType.int, 2, 3, 4, 5)
        property_store.write_item(db_property)

        # Read the property from the PropertyStore file
        db_property_file = property_store.item_at_index(db_property.index)

        # Assert that the values are the same
        self.assertEquals(db_property, db_property_file)

    def test_write_read_2_properties(self):
        """
        Tests when 2 properties are written after 1 property
        to the PropertyStore
        """
        property_store = PropertyStore()

        # Create one property and write it to the PropertyStore
        property1 = Property(1, False, Property.PropertyType.bool, 2, 3, 4, 5)
        property_store.write_item(property1)

        # Create 2 properties and add them to the PropertyStore
        property2 = Property(2, False, Property.PropertyType.char, 4, 6, 8, 10)
        property3 = Property(9, True, Property.PropertyType.float, 8, 7, 6, 5)
        property_store.write_item(property2)
        property_store.write_item(property3)

        # Read the properties from the PropertyStore file
        property1_file = property_store.item_at_index(property1.index)
        property2_file = property_store.item_at_index(property2.index)
        property3_file = property_store.item_at_index(property3.index)

        # Make sure their values are the same
        self.assertEquals(property1, property1_file)
        self.assertEquals(property2, property2_file)
        self.assertEquals(property3, property3_file)

    def test_overwrite_property(self):
        """
        Tests that overwriting a property in a database with 3 properties works
        """
        property_store = PropertyStore()

        # Create 3 properties
        property1 = Property(1, False, Property.PropertyType.short, 2, 3, 4, 5)
        property2 = Property(2, True, Property.PropertyType.string, 4, 6, 8, 10)
        property3 = Property(9, False, Property.PropertyType.double, 8, 7, 6, 5)

        # Write them to the property_store
        property_store.write_item(property1)
        property_store.write_item(property2)
        property_store.write_item(property3)

        # Verify that they are in the store as expected
        property1_file = property_store.item_at_index(property1.index)
        self.assertEquals(property1, property1_file)

        property2_file = property_store.item_at_index(property2.index)
        self.assertEquals(property2, property2_file)

        property3_file = property_store.item_at_index(property3.index)
        self.assertEquals(property3, property3_file)

        # Create a new property2 and overwrite the old property2
        new_property2 = Property(3, False, Property.PropertyType.stringArray,
                                 6, 9, 12, 15)
        property_store.write_item(new_property2)

        # Verify that the data is still as expected
        property1_file = property_store.item_at_index(property1.index)
        self.assertEquals(property1, property1_file)

        new_property2_file = \
            property_store.item_at_index(new_property2.index)
        self.assertEquals(new_property2, new_property2_file)

        property3_file = property_store.item_at_index(property3.index)
        self.assertEquals(property3, property3_file)

    def test_delete_property(self):
        """
        Tests that deleting 2 properties in a database with 3 properties works
        """
        property_store = PropertyStore()

        # Create 3 properties
        property1 = Property(1, False, Property.PropertyType.short, 2, 3, 4, 5)
        property2 = Property(2, True, Property.PropertyType.string, 4, 6, 8, 10)
        property3 = Property(9, False, Property.PropertyType.double, 8, 7, 6, 5)

        # Write them to the property_store
        property_store.write_item(property1)
        property_store.write_item(property2)
        property_store.write_item(property3)

        # Verify that they are in the store as expected
        property1_file = property_store.item_at_index(property1.index)
        self.assertEquals(property1, property1_file)

        property2_file = property_store.item_at_index(property2.index)
        self.assertEquals(property2, property2_file)

        property3_file = property_store.item_at_index(property3.index)
        self.assertEquals(property3, property3_file)

        # Delete properties 1 and 3
        property_store.delete_item(property1)
        property_store.delete_item(property3)

        # Create properties 1 and 3 with zeroed out values
        zero_property1 = Property(property1.index, False,
                                  Property.PropertyType.undefined, 0, 0, 0, 0)
        zero_property3 = Property(property3.index, False,
                                  Property.PropertyType.undefined, 0, 0, 0, 0)

        # Verify deleted property is zeroed out
        del_property1_file = property_store.item_at_index(property1.index)
        self.assertEquals(zero_property1, del_property1_file)

        # Verify unaffected property is as expected
        property2_file = property_store.item_at_index(property2.index)
        self.assertEquals(property2, property2_file)

        # Verify deleted property is zeroed out
        del_property3_file = property_store.item_at_index(property3.index)
        self.assertEquals(zero_property3, del_property3_file)


