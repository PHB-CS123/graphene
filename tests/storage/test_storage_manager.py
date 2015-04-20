import unittest

from graphene.storage import (StorageManager, GrapheneStore, Property)
from graphene.storage.intermediate import (GeneralNameManager)


class TestStorageManagerMethods(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True
        self.sm = StorageManager()

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        #graphene_store.remove_test_datafiles()

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
