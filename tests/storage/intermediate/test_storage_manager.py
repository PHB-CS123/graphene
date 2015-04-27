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
        with self.assertRaises(TypeDoesNotExistException):
            self.sm.get_type_data("asdf")

    def test_insert_node(self):
        t = self.sm.create_type("T", (("a", "int"), ("b", "string")))
        node, props = self.sm.insert_node(t, ((Property.PropertyType.int, 3),(Property.PropertyType.string, "a")))
        assert self.sm.get_node_type(node) == t

        assert node.propId == props[0].index
        assert self.sm.get_property_value(props[0]) == 3
        assert self.sm.get_property_value(props[1]) == "a"

        assert node.relId == 0

    def test_create_type(self):
        schema = ( ("name", "string"), ("age", "int"), ("address", "string") )
        t = self.sm.create_type("Person", schema)
        type_name = self.sm.type_name_manager.read_name_at_index(t.nameId)
        assert type_name == "Person"
        type_types = []
        type_types.append(self.sm.type_type_manager.get_item_at_index(t.firstType))
        while type_types[-1].nextType != 0:
            type_types.append(self.sm.type_type_manager.get_item_at_index(type_types[-1].nextType))
        for i, tt in enumerate(type_types):
            tt_name = self.sm.type_type_name_manager.read_name_at_index(tt.typeName)
            tt_type = tt.propertyType.name
            s_name, s_type = schema[i]
            assert tt_name == s_name
            assert tt_type == s_type

    def test_create_type_with_nodes(self):
        t = self.sm.create_type("T", (("a", "int"),("c", "string"),))
        n1, p1 = self.sm.insert_node(t, ((Property.PropertyType.int, 1),(Property.PropertyType.string, "a")))
        n2, p2 = self.sm.insert_node(t, ((Property.PropertyType.int, 2),(Property.PropertyType.string, "b")))
        n3, p3 = self.sm.insert_node(t, ((Property.PropertyType.int, 3),(Property.PropertyType.string, "c")))
        n1i, p1i = n1.index, [p1[0].index, p1[1].index]
        n2i, p2i = n2.index, [p2[0].index, p2[1].index]
        n3i, p3i = n3.index, [p3[0].index, p3[1].index]
        idx = t.index
        self.sm.delete_type("T")
        assert self.sm.type_manager.get_item_at_index(idx) is None
        with self.assertRaises(TypeDoesNotExistException):
            self.sm.get_type_data("T")
        assert self.sm.node_manager.get_item_at_index(n1i) is None
        assert self.sm.node_manager.get_item_at_index(n2i) is None
        assert self.sm.node_manager.get_item_at_index(n3i) is None
        for i in p1i:
            assert self.sm.property_manager.get_item_at_index(i) is None
        for i in p2i:
            assert self.sm.property_manager.get_item_at_index(i) is None
        for i in p3i:
            assert self.sm.property_manager.get_item_at_index(i) is None

    def test_create_type_exists(self):
        self.sm.create_type("T", (("a", "int"),))
        with self.assertRaises(TypeAlreadyExistsException):
            self.sm.create_type("T", (("a", "int"),))

    def test_delete_type(self):
        schema = ( ("name", "string"), ("age", "int"), ("address", "string") )
        t = self.sm.create_type("Person", schema)
        idx = t.index
        self.sm.delete_type("Person")
        assert self.sm.type_manager.get_item_at_index(idx) is None
        with self.assertRaises(TypeDoesNotExistException):
            self.sm.get_type_data("Person")

    def test_convert_to_value(self):
        assert self.sm.convert_to_value('"a"', Property.PropertyType.string) == "a"
        assert self.sm.convert_to_value('true', Property.PropertyType.bool) == True
        assert self.sm.convert_to_value('false', Property.PropertyType.bool) == False
        assert self.sm.convert_to_value('34', Property.PropertyType.int) == 34
        assert self.sm.convert_to_value('-34', Property.PropertyType.int) == -34
