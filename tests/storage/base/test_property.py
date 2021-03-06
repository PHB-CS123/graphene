import unittest

from graphene.storage.base.property import *


class TestPropertyMethods(unittest.TestCase):
    def test_empty_init(self):
        """
        Tests that initializing a property with no arguments, uses the
        default values below.
        """
        db_property = Property()

        self.assertEquals(db_property.index, 0)
        self.assertEquals(db_property.inUse, True)
        self.assertEquals(db_property.type, Property.PropertyType.undefined)
        self.assertEquals(db_property.nameId, 0)
        self.assertEquals(db_property.propBlockId, 0)
        self.assertEquals(db_property.prevPropId, 0)
        self.assertEquals(db_property.nextPropId, 0)

    def test_init(self):
        """
        Tests that initializing a property with a set of values stores
        those values properly
        """
        # Property values
        index = 1
        in_use = False
        prop_type = Property.PropertyType.int
        key_index_id = 2
        prev_prop_id = 3
        next_prop_id = 4
        prop_block_id = 262144

        # Create property
        db_property = Property(index, in_use, prop_type, key_index_id,
                               prev_prop_id, next_prop_id, prop_block_id)

        # Check values
        self.assertEquals(db_property.index, index)
        self.assertEquals(db_property.inUse, in_use)
        self.assertEquals(db_property.type, prop_type)
        self.assertEquals(db_property.nameId, key_index_id)
        self.assertEquals(db_property.propBlockId, prop_block_id)
        self.assertEquals(db_property.prevPropId, prev_prop_id)
        self.assertEquals(db_property.nextPropId, next_prop_id)

    def test_eq(self):
        """
        Tests that the == operator returns True when two properties are equal
        and False when they are not. Tests != when checking not equals.
        """
        property1 = Property(1, True, Property.PropertyType.int, 2, 3, 4, 5)
        property2 = Property(1, True, Property.PropertyType.int, 2, 3, 4, 5)
        property3 = Property(9, False, Property.PropertyType.long, 8, 7, 6, 5)

        self.assertEqual(property1, property2)
        self.assertNotEqual(property1, property3)
        self.assertNotEqual(property2, property3)
        self.assertNotEqual(property1, 1)

    def test_property_type_determination(self):
        """
        Tests that the is_<property_type> returns appropriate results
        """
        prop1 = Property(1, True, Property.PropertyType.int, 2, 3, 4, 5)
        prop2 = Property(2, True, Property.PropertyType.string, 3, 4, 5, 6)
        prop3 = Property(3, True, Property.PropertyType.intArray, 3, 4, 5, 6)

        self.assertFalse(prop1.is_array())
        self.assertFalse(prop1.is_string())
        self.assertTrue(prop1.is_primitive())

        self.assertFalse(prop2.is_array())
        self.assertTrue(prop2.is_string())
        self.assertFalse(prop2.is_primitive())

        self.assertTrue(prop3.is_array())
        self.assertFalse(prop3.is_string())
        self.assertFalse(prop3.is_primitive())

    def test_property_type_methods(self):
        self.assertFalse(Property.PropertyType.is_array(Property.PropertyType.int))
        self.assertFalse(Property.PropertyType.is_string(Property.PropertyType.int))
        self.assertTrue(Property.PropertyType.is_primitive(Property.PropertyType.int))
        self.assertTrue(Property.PropertyType.is_numerical(Property.PropertyType.int))

        self.assertFalse(Property.PropertyType.is_numerical(Property.PropertyType.bool))
        self.assertFalse(Property.PropertyType.is_numerical(Property.PropertyType.char))

        self.assertTrue(Property.PropertyType.is_array(Property.PropertyType.intArray))
        self.assertFalse(Property.PropertyType.is_string(Property.PropertyType.intArray))
        self.assertFalse(Property.PropertyType.is_primitive(Property.PropertyType.intArray))
        self.assertFalse(Property.PropertyType.is_numerical(Property.PropertyType.intArray))

        self.assertFalse(Property.PropertyType.is_array(Property.PropertyType.string))
        self.assertTrue(Property.PropertyType.is_string(Property.PropertyType.string))
        self.assertFalse(Property.PropertyType.is_primitive(Property.PropertyType.string))
        self.assertFalse(Property.PropertyType.is_numerical(Property.PropertyType.string))

        self.assertFalse(Property.PropertyType.is_array(Property.PropertyType.undefined))
        self.assertFalse(Property.PropertyType.is_string(Property.PropertyType.undefined))
        self.assertFalse(Property.PropertyType.is_primitive(Property.PropertyType.undefined))
        self.assertFalse(Property.PropertyType.is_numerical(Property.PropertyType.undefined))

        with self.assertRaises(AssertionError):
            Property.PropertyType.get_base_type(Property.PropertyType.int)
            Property.PropertyType.get_array_type(Property.PropertyType.intArray)
        self.assertEqual(Property.PropertyType.get_base_type(Property.PropertyType.intArray), Property.PropertyType.int)
        self.assertEqual(Property.PropertyType.get_array_type(Property.PropertyType.int), Property.PropertyType.intArray)
