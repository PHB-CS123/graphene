import unittest

from graphene.utils.conversion import TypeConversion
from graphene.storage import Property

class TestTypeConversion(unittest.TestCase):
    def test_convert_to_value(self):
        self.assertEquals(TypeConversion.convert_to_value('"a"', Property.PropertyType.string), "a")
        self.assertEquals(TypeConversion.convert_to_value('true', Property.PropertyType.bool), True)
        self.assertEquals(TypeConversion.convert_to_value('false', Property.PropertyType.bool), False)
        self.assertEquals(TypeConversion.convert_to_value('34', Property.PropertyType.int), 34)
        self.assertEquals(TypeConversion.convert_to_value('-34', Property.PropertyType.int), -34)
        self.assertEquals(TypeConversion.convert_to_value('[]', Property.PropertyType.intArray), [])
        self.assertEquals(TypeConversion.convert_to_value('[3]', Property.PropertyType.intArray), [3])

    def test_get_type_type_of_string(self):
        self.assertEquals(TypeConversion.get_type_type_of_string('"a"'), Property.PropertyType.string)
        self.assertEquals(TypeConversion.get_type_type_of_string('true'), Property.PropertyType.bool)
        self.assertEquals(TypeConversion.get_type_type_of_string('false'), Property.PropertyType.bool)
        self.assertEquals(TypeConversion.get_type_type_of_string('34'), Property.PropertyType.int)
        self.assertEquals(TypeConversion.get_type_type_of_string('3.4'), Property.PropertyType.undefined)
        self.assertEquals(TypeConversion.get_type_type_of_string('-34'), Property.PropertyType.int)
        # Empty arrays are undefined because they could have anything
        self.assertEquals(TypeConversion.get_type_type_of_string('[]'), Property.PropertyType.undefined)
        self.assertEquals(TypeConversion.get_type_type_of_string('[3]'), Property.PropertyType.intArray)
        # Arrays with inconsistent types are also undefined
        self.assertEquals(TypeConversion.get_type_type_of_string('[3, "str"]'), Property.PropertyType.undefined)
