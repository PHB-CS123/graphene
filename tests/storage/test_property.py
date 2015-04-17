import unittest

from graphene.storage.property import *


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
        prop_block_id = 3
        prev_prop_id = 4
        next_prop_id = 5

        # Create property
        db_property = Property(index, in_use, prop_type, key_index_id,
                               prop_block_id, prev_prop_id, next_prop_id)

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
        and False when they are not
        """
        property1 = Property(1, True, Property.PropertyType.int, 2, 3, 4, 5)
        property2 = Property(1, True, Property.PropertyType.int, 2, 3, 4, 5)
        property3 = Property(9, False, Property.PropertyType.long, 8, 7, 6, 5)

        self.assertTrue(property1 == property2)
        self.assertFalse(property1 == property3)
        self.assertFalse(property2 == property3)
        self.assertFalse(property1 == 1)
