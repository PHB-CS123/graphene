import unittest

from graphene.errors.storage_manager_errors import *
from graphene.storage import (StorageManager, GrapheneStore, Property,
                              Relationship, Node)
from graphene.storage.base.general_store import EOF


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
            if "[]" in s_type:
                # The type name has Array in it but the way the schema reads it
                # is with a []
                s_type = s_type.replace("[]", "Array")
            self.assertEquals(tt_name, s_name)
            self.assertEquals(tt_type, s_type)

    def test_create_node_type(self):
        schema = ( ("name", "string"), ("age", "int"), ("address", "string"),
                    ("phones", "string[]") )
        t = self.sm.create_node_type("Person", schema)
        type_name = self.sm.nodeTypeNameManager.read_name_at_index(t.nameId)
        self.assertEquals(type_name, "Person")

        type_types = self.get_all_type_types(t)
        self.check_type_types_with_schema(type_types, schema)

    def test_create_type_with_nodes(self):
        t = self.sm.create_node_type("T", (("a", "int"),("c", "string"),
            ("d", "int[]")))
        n1, p1 = self.sm.insert_node(t, ((Property.PropertyType.int, 1),
                                         (Property.PropertyType.string, "a"),
                                         (Property.PropertyType.intArray, [1])))
        n2, p2 = self.sm.insert_node(t, ((Property.PropertyType.int, 2),
                                         (Property.PropertyType.string, "b"),
                                         (Property.PropertyType.intArray, [2])))
        n3, p3 = self.sm.insert_node(t, ((Property.PropertyType.int, 3),
                                         (Property.PropertyType.string, "c"),
                                         (Property.PropertyType.intArray, [3])))
        n1i, p1i = n1.index, [p1[0].index, p1[1].index]
        n2i, p2i = n2.index, [p2[0].index, p2[1].index]
        n3i, p3i = n3.index, [p3[0].index, p3[1].index]
        idx = t.index
        self.sm.delete_node_type("T")
        item = self.sm.nodeTypeManager.get_item_at_index(idx)
        self.assertTrue(item is None or item is EOF)
        with self.assertRaises(TypeDoesNotExistException):
            self.sm.get_node_data("T")
        item = self.sm.node_manager.get_item_at_index(n1i)
        self.assertTrue(item is None or item is EOF)
        item = self.sm.node_manager.get_item_at_index(n2i)
        self.assertTrue(item is None or item is EOF)
        item = self.sm.node_manager.get_item_at_index(n3i)
        self.assertTrue(item is None or item is EOF)

        for i in p1i:
            item = self.sm.property_manager.get_item_at_index(i)
            self.assertTrue(item is None or item is EOF)
        for i in p2i:
            item = self.sm.property_manager.get_item_at_index(i)
            self.assertTrue(item is None or item is EOF)
        for i in p3i:
            item = self.sm.property_manager.get_item_at_index(i)
            self.assertTrue(item is None or item is EOF)

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

    def test_create_rel_type_exists(self):
        self.sm.create_relationship_type("R", (("a", "int"),))
        with self.assertRaises(TypeAlreadyExistsException):
            self.sm.create_relationship_type("R", (("a", "int"),))

    def test_delete_node_type(self):
        schema = ( ("name", "string"), ("age", "int"), ("address", "string") )
        t = self.sm.create_node_type("Person", schema)
        idx = t.index
        self.sm.delete_node_type("Person")
        item = self.sm.nodeTypeManager.get_item_at_index(idx)
        self.assertTrue(item is None or item is EOF)
        with self.assertRaises(TypeDoesNotExistException):
            self.sm.get_node_data("Person")

    def test_delete_relationship_type(self):
        schema = ( ("a", "string"), ("b", "int"), ("c", "string") )
        t = self.sm.create_relationship_type("R", schema)
        idx = t.index
        self.sm.delete_relationship_type("R")
        item = self.sm.relTypeManager.get_item_at_index(idx)
        self.assertTrue(item is None or item is EOF)
        with self.assertRaises(TypeDoesNotExistException):
            self.sm.get_relationship_data("R")

    def test_insert_relation(self):
        t = self.sm.create_node_type("T", (("a", "int"),))
        r = self.sm.create_relationship_type("R",
            (("a", "int"), ("b", "int"), ("c", "string")))
        n1, p1 = self.sm.insert_node(t, ((Property.PropertyType.int, 3),))
        n2, p2 = self.sm.insert_node(t, ((Property.PropertyType.int, 4),))

        inserted_rel = self.sm.insert_relation(r,
            ((Property.PropertyType.int, 1),) * 2 + \
            ((Property.PropertyType.string, "a"),), n1, n2)
        rel_idx = inserted_rel.index
        rel, props = self.sm.relprop[rel_idx]

        self.assertEquals(rel.relType, r.index)
        self.assertEquals(rel.direction, Relationship.Direction.right)
        self.assertEquals(rel.firstNodeId, n1.index)
        self.assertEquals(rel.secondNodeId, n2.index)
        self.assertEquals(rel.firstPrevRelId, 0)
        self.assertEquals(rel.firstNextRelId, 0)
        self.assertEquals(rel.propId, props[0].index)

        # Check that nodes were updated
        self.assertEquals(n1.relId, rel_idx)
        self.assertEquals(n2.relId, rel_idx)

    def test_multiple_relations(self):
        t = self.sm.create_node_type("T", (("a", "int"),))
        r = self.sm.create_relationship_type("R", ())
        n1, p1 = self.sm.insert_node(t, ((Property.PropertyType.int, 3),))
        n2, p2 = self.sm.insert_node(t, ((Property.PropertyType.int, 4),))
        n3, p3 = self.sm.insert_node(t, ((Property.PropertyType.int, 5),))
        n4, p4 = self.sm.insert_node(t, ((Property.PropertyType.int, 6),))

        ## Initial Relation
        inserted_rel1 = self.sm.insert_relation(r, (), n1, n2)
        rel1_idx = inserted_rel1.index
        rel1, props1 = self.sm.relprop[rel1_idx]

        self.assertEquals(rel1.firstPrevRelId, 0)
        self.assertEquals(rel1.firstNextRelId, 0)

        # Check that nodes were updated
        self.assertEquals(n1.relId, rel1_idx)
        self.assertEquals(n2.relId, rel1_idx)

        ## Relation where source is source of previous relation
        inserted_rel2 = self.sm.insert_relation(r, (), n1, n3)
        rel2_idx = inserted_rel2.index
        rel2, props2 = self.sm.relprop[rel2_idx]

        # Update this since it was changed in the cache
        rel1, props1 = self.sm.relprop[rel1_idx]

        self.assertEquals(rel2.firstNextRelId, rel1_idx)
        self.assertEquals(rel1.firstPrevRelId, rel2_idx)

        # Check that nodes were updated
        self.assertEquals(n1.relId, rel2_idx)
        self.assertEquals(n3.relId, rel2_idx)

        ## Relation where destination is source of previous relation
        inserted_rel3 = self.sm.insert_relation(r, (), n4, n1)
        rel3_idx = inserted_rel3.index
        rel3, props3 = self.sm.relprop[rel3_idx]

        # Update these since they were changed in the cache
        rel2, props2 = self.sm.relprop[rel2_idx]
        rel1, props1 = self.sm.relprop[rel1_idx]

        self.assertEquals(rel3.secondNextRelId, rel2_idx)
        self.assertEquals(rel2.firstNextRelId, rel1_idx)
        self.assertEquals(rel2.firstPrevRelId, rel3_idx)

        # Check that nodes were updated
        self.assertEquals(n1.relId, rel3_idx)
        self.assertEquals(n4.relId, rel3_idx)

        ## Relation where source is destination of previous relation
        inserted_rel4 = self.sm.insert_relation(r, (), n2, n3)
        rel4_idx = inserted_rel4.index
        rel4, props4 = self.sm.relprop[rel4_idx]

        # Update these since they were changed in the cache
        rel3, props3 = self.sm.relprop[rel3_idx]
        rel2, props2 = self.sm.relprop[rel2_idx]
        rel1, props1 = self.sm.relprop[rel1_idx]

        self.assertEquals(rel4.firstNextRelId, rel1_idx)
        self.assertEquals(rel1.secondPrevRelId, rel4_idx)

        # Check that nodes were updated
        self.assertEquals(n2.relId, rel4_idx)
        self.assertEquals(n3.relId, rel4_idx)

        ## Relation where destination is destination of previous relation
        inserted_rel5 = self.sm.insert_relation(r, (), n4, n3)
        rel5_idx = inserted_rel5.index
        rel5, props5 = self.sm.relprop[rel5_idx]

        # Update these since they were changed in the cache
        rel4, props4 = self.sm.relprop[rel4_idx]
        rel3, props3 = self.sm.relprop[rel3_idx]
        rel2, props2 = self.sm.relprop[rel2_idx]
        rel1, props1 = self.sm.relprop[rel1_idx]

        self.assertEquals(rel5.secondNextRelId, rel4_idx)
        self.assertEquals(rel4.secondNextRelId, rel2_idx)
        self.assertEquals(rel4.secondPrevRelId, rel5_idx)

        # Check that nodes were updated
        self.assertEquals(n4.relId, rel5_idx)
        self.assertEquals(n3.relId, rel5_idx)
