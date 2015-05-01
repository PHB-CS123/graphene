import unittest

from graphene.errors.storage_manager_errors import *
from graphene.storage import (StorageManager, GrapheneStore, Property)


class TestStorageManagerMethods(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        self.sm = StorageManager()

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_get_empty_type_data(self):
        """
        Test the get_type_data method when no types exist
        """
        with self.assertRaises(TypeDoesNotExistException):
            self.sm.get_type_data("asdf", True)

    def test_insert_node(self):
        t = self.sm.create_node_type("T", (("a", "int"), ("b", "string")))
        node, props = self.sm.insert_node(t, ((Property.PropertyType.int, 3),
                                              (Property.PropertyType.string, "a")))
        self.assertEquals(self.sm.get_node_type(node), t)

        self.assertEquals(node.propId, props[0].index)
        self.assertEquals(self.sm.get_property_value(props[0]), 3)
        self.assertEquals(self.sm.get_property_value(props[1]), "a")

        self.assertEquals(node.relId, 0)

    def get_all_type_types(self, t):
        """
        Helper function for getting all of the type types of a certain node
        type.

        :param t: A general (Node) type
        :return: [type_types]
        """
        type_types = [
            self.sm.nodeTypeTypeManager.get_item_at_index(t.firstType)]
        while type_types[-1].nextType != 0:
            type_types.append(self.sm.nodeTypeTypeManager.
                              get_item_at_index(type_types[-1].nextType))
        return type_types

    def check_type_types_with_schema(self, type_types, schema):
        """
        Helper function for checking that a node's type types match its schema.

        :param type_types: a given type's property types
        :param schema: a given type's true property types
        """
        for i, tt in enumerate(type_types):
            tt_name = self.sm.nodeTypeTypeNameManager. \
                read_name_at_index(tt.typeName)
            tt_type = tt.propertyType.name
            s_name, s_type = schema[i]
            self.assertEquals(tt_name, s_name)
            self.assertEquals(tt_type, s_type)

    def test_create_node_type(self):
        schema = ( ("name", "string"), ("age", "int"), ("address", "string") )
        t = self.sm.create_node_type("Person", schema)
        type_name = self.sm.nodeTypeNameManager.read_name_at_index(t.nameId)
        self.assertEquals(type_name, "Person")

        type_types = self.get_all_type_types(t)
        self.check_type_types_with_schema(type_types, schema)

    def test_create_type_with_nodes(self):
        t = self.sm.create_node_type("T", (("a", "int"),("c", "string"),))
        n1, p1 = self.sm.insert_node(t, ((Property.PropertyType.int, 1),
                                         (Property.PropertyType.string, "a")))
        n2, p2 = self.sm.insert_node(t, ((Property.PropertyType.int, 2),
                                         (Property.PropertyType.string, "b")))
        n3, p3 = self.sm.insert_node(t, ((Property.PropertyType.int, 3),
                                         (Property.PropertyType.string, "c")))
        n1i, p1i = n1.index, [p1[0].index, p1[1].index]
        n2i, p2i = n2.index, [p2[0].index, p2[1].index]
        n3i, p3i = n3.index, [p3[0].index, p3[1].index]
        idx = t.index
        self.sm.delete_node_type("T")
        self.assertEquals(self.sm.nodeTypeManager.get_item_at_index(idx), None)
        with self.assertRaises(TypeDoesNotExistException):
            self.sm.get_node_data("T")
        self.assertEquals(self.sm.node_manager.get_item_at_index(n1i), None)
        self.assertEquals(self.sm.node_manager.get_item_at_index(n2i), None)
        self.assertEquals(self.sm.node_manager.get_item_at_index(n3i), None)
        for i in p1i:
            self.assertEquals(self.sm.property_manager.get_item_at_index(i), None)
        for i in p2i:
            self.assertEquals(self.sm.property_manager.get_item_at_index(i), None)
        for i in p3i:
            self.assertEquals(self.sm.property_manager.get_item_at_index(i), None)

    def test_create_multiple_types(self):
        """
        Make sure the first and second type names, type types, and type type
        names are recorded correctly.
        """
        schema1 = (("a", "string"), ("b", "int"), )
        schema2 = (("c", "int"), ("d", "string"), )

        t1 = self.sm.create_node_type("T", schema1)
        t2 = self.sm.create_node_type("U", schema2)

        self.assertEquals(self.sm.nodeTypeNameManager.read_name_at_index(
            t1.nameId), "T")
        self.assertEquals(self.sm.nodeTypeNameManager.read_name_at_index(
            t2.nameId), "U")

        t1_tts, t2_tts = self.get_all_type_types(t1), self.get_all_type_types(t2)
        self.check_type_types_with_schema(t1_tts, schema1)
        self.check_type_types_with_schema(t2_tts, schema2)

    def test_create_node_type_exists(self):
        self.sm.create_node_type("T", (("a", "int"),))
        with self.assertRaises(TypeAlreadyExistsException):
            self.sm.create_node_type("T", (("a", "int"),))

    def test_delete_node_type(self):
        schema = ( ("name", "string"), ("age", "int"), ("address", "string") )
        t = self.sm.create_node_type("Person", schema)
        idx = t.index
        self.sm.delete_node_type("Person")
        self.assertEquals(self.sm.nodeTypeManager.get_item_at_index(idx), None)
        with self.assertRaises(TypeDoesNotExistException):
            self.sm.get_node_data("Person")

    def test_convert_to_value(self):
        self.assertEquals(self.sm.convert_to_value('"a"', Property.PropertyType.string), "a")
        self.assertEquals(self.sm.convert_to_value('true', Property.PropertyType.bool), True)
        self.assertEquals(self.sm.convert_to_value('false', Property.PropertyType.bool), False)
        self.assertEquals(self.sm.convert_to_value('34', Property.PropertyType.int), 34)
        self.assertEquals(self.sm.convert_to_value('-34', Property.PropertyType.int), -34)
