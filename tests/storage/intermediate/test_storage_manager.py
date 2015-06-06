import unittest

from graphene.errors.storage_manager_errors import *
from graphene.storage import (StorageManager, GrapheneStore, Property,
                              Relationship, Node)
from graphene.storage.intermediate.node_property import NodeProperty
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
        del self.sm
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def assertIsNoneOrEOF(self, item):
        """
        Since values at the end of a file are still nonexistent, both None and
        EOF are OK
        """
        self.assertTrue(item is None or item is EOF)

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
        self.assertIsNoneOrEOF(item)
        with self.assertRaises(TypeDoesNotExistException):
            self.sm.get_node_data("T")
        item = self.sm.node_manager.get_item_at_index(n1i)
        self.assertIsNoneOrEOF(item)
        item = self.sm.node_manager.get_item_at_index(n2i)
        self.assertIsNoneOrEOF(item)
        item = self.sm.node_manager.get_item_at_index(n3i)
        self.assertIsNoneOrEOF(item)

        for i in p1i:
            item = self.sm.property_manager.get_item_at_index(i)
            self.assertIsNoneOrEOF(item)
        for i in p2i:
            item = self.sm.property_manager.get_item_at_index(i)
            self.assertIsNoneOrEOF(item)
        for i in p3i:
            item = self.sm.property_manager.get_item_at_index(i)
            self.assertIsNoneOrEOF(item)

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
        self.assertIsNoneOrEOF(item)
        with self.assertRaises(TypeDoesNotExistException):
            self.sm.get_node_data("Person")

    def test_delete_relationship_type(self):
        schema = ( ("a", "string"), ("b", "int"), ("c", "string") )
        t = self.sm.create_relationship_type("R", schema)
        idx = t.index
        self.sm.delete_relationship_type("R")
        item = self.sm.relTypeManager.get_item_at_index(idx)
        self.assertIsNoneOrEOF(item)
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


    def test_delete_relation(self):
        t = self.sm.create_node_type("T", (("a", "int"),))
        n1, p1 = self.sm.insert_node(t, ((Property.PropertyType.int, 2),))
        n2, p2 = self.sm.insert_node(t, ((Property.PropertyType.int, 3),))
        n3, p3 = self.sm.insert_node(t, ((Property.PropertyType.int, 5),))

        r = self.sm.create_relationship_type("R",
            (("b", "int"), ("c", "string"), ("d", "int[]")))

        r1i = self.sm.insert_relation(r,
            ((Property.PropertyType.int, 6),(Property.PropertyType.string, "a"),
                (Property.PropertyType.intArray, [1,2])),
            n1, n2).index
        self.assertEqual(n1.relId, r1i)
        self.assertEqual(n2.relId, r1i)

        r2i = self.sm.insert_relation(r,
            ((Property.PropertyType.int, 10),(Property.PropertyType.string, "b"),
                (Property.PropertyType.intArray, [3,4])),
            n3, n1).index
        r1, rp1 = self.sm.relprop[r1i] # update relation 1
        r2, rp2 = self.sm.relprop[r2i]
        self.assertEqual(n3.relId, r2i)
        self.assertEqual(n1.relId, r2i)
        self.assertEqual(r1.firstPrevRelId, r2i)
        self.assertEqual(r2.secondNextRelId, r1i)

        r3i = self.sm.insert_relation(r,
            ((Property.PropertyType.int, 15),(Property.PropertyType.string, "c"),
                (Property.PropertyType.intArray, [5,6])),
            n2, n3).index
        r1, rp1 = self.sm.relprop[r1i] # update relation 1
        r2, rp2 = self.sm.relprop[r2i] # update relation 2
        r3, rp3 = self.sm.relprop[r3i]
        self.assertEqual(n2.relId, r3i)
        self.assertEqual(n3.relId, r3i)
        self.assertEqual(r2.firstPrevRelId, r3i)
        self.assertEqual(r1.secondPrevRelId, r3i)
        self.assertEqual(r3.firstNextRelId, r1i)
        self.assertEqual(r3.secondNextRelId, r2i)

        del self.sm.relprop[r2i]

        r1, rp1 = self.sm.relprop[r1i] # update relation 1
        r3, rp3 = self.sm.relprop[r3i] # update relation 3
        n1, p1 = self.sm.nodeprop[n1.index]
        n2, p2 = self.sm.nodeprop[n2.index]
        n3, p3 = self.sm.nodeprop[n3.index]

        self.assertEqual(n1.relId, r1i)
        self.assertEqual(n3.relId, r3i)

        # Ensure every property is now None in the manager (i.e. it was deleted)
        map(self.assertIsNoneOrEOF,
            map(self.sm.property_manager.get_item_at_index,
                map(lambda p: p.index, rp2)))
        self.assertIsNoneOrEOF(self.sm.prop_string_manager.read_name_at_index(rp2[1].propBlockId))
        self.assertIsNoneOrEOF(self.sm.array_manager.read_array_at_index(rp2[2].propBlockId))

        self.assertEqual(r3.secondNextRelId, 0)
        self.assertEqual(r1.firstPrevRelId, 0)

        del self.sm.relprop[r3i]
        r1, rp1 = self.sm.relprop[r1i] # update relation 1
        n1, p1 = self.sm.nodeprop[n1.index]
        n2, p2 = self.sm.nodeprop[n2.index]
        n3, p3 = self.sm.nodeprop[n3.index]

        map(self.assertIsNoneOrEOF,
            map(self.sm.property_manager.get_item_at_index,
                map(lambda p: p.index, rp3)))
        self.assertIsNoneOrEOF(self.sm.prop_string_manager.read_name_at_index(rp3[1].propBlockId))
        self.assertIsNoneOrEOF(self.sm.array_manager.read_array_at_index(rp3[2].propBlockId))

        self.assertEqual(n3.relId, 0)
        self.assertEqual(n2.relId, r1i)
        self.assertEqual(r1.secondPrevRelId, 0)

        del self.sm.relprop[r1i]
        n1, p1 = self.sm.nodeprop[n1.index]
        n2, p2 = self.sm.nodeprop[n2.index]

        map(self.assertIsNoneOrEOF,
            map(self.sm.property_manager.get_item_at_index,
                map(lambda p: p.index, rp1)))
        self.assertIsNoneOrEOF(self.sm.prop_string_manager.read_name_at_index(rp1[1].propBlockId))
        self.assertIsNoneOrEOF(self.sm.array_manager.read_array_at_index(rp1[2].propBlockId))

        self.assertEqual(n1.relId, 0)
        self.assertEqual(n2.relId, 0)

    def test_update_nodes_simple(self):
        """
        Test that updating a node's properties works properly, in a 1 property
        case
        """
        pass
        # t = self.sm.create_node_type("T", (("a", "int"),))
        # # Create 3 nodes of type T
        # n1, p1 = self.sm.insert_node(t, ((Property.PropertyType.int, 2),))
        # n2, p2 = self.sm.insert_node(t, ((Property.PropertyType.int, 3),))
        # n3, p3 = self.sm.insert_node(t, ((Property.PropertyType.int, 5),))
        #
        # # Update nodes 1 and 3 with value 10
        # update = {"a": 10}
        # # Create nodeprops for update nodes
        # nodeprop1 = NodeProperty(n1, p1, t, "T")
        # nodeprop3 = NodeProperty(n3, p3, t, "T")
        # nodeprops = [nodeprop1, nodeprop3]
        # import pytest
        # pytest.set_trace()
        # self.sm.update_nodes(nodeprops, update)
        # # Check that values are updated
        # n1_f, p1_f = self.sm.nodeprop[n1.index]
        # n2_f, p2_f = self.sm.nodeprop[n2.index]
        # n3_f, p3_f = self.sm.nodeprop[n3.index]
        #
        # self.assertEquals(p1_f[0].propBlockId, 10)
        # self.assertEquals(p3_f[0].propBlockId, 10)
        # # Check that untouched values are the same
        # self.assertEquals(p2_f[0].propBlockId, 3)

    def test_update_relations(self):
        """
        Test that updating a relation's properties works properly
        """
        # TODO
        pass

    def test_names_to_ids(self):
        """
        Test that getting IDs from node/relationship property names works
        """
        # Test node type item indexes are read
        t = self.sm.create_node_type("T", (("a", "int"), ("c", "string"),
                                           ("d", "int[]")))
        t_type_idx = t.firstType
        t_type_idxs = [t_type_idx]
        while t_type_idx != 0:
            t_type_idx = self.sm.nodeTypeTypeManager.\
                get_item_at_index(t_type_idx).nextType
            t_type_idxs.append(t_type_idx)
        # Update dictionary
        u_dict = {"a": 1, "c": 2, "d": 3}
        # Update dictionary with names replaced by IDs
        u_ids_dict = {1: 1, 2: 2, 3: 3}
        self.assertEquals(self.sm.names_to_ids(u_dict, True), u_ids_dict)

        # Test node type item indexes are read
        schema = (("a", "string"), ("b", "int"), ("c", "string"))
        t = self.sm.create_relationship_type("R", schema)
        t_type_idx = t.firstType
        t_type_idxs = [t_type_idx]
        while t_type_idx != 0:
            t_type_idx = self.sm.nodeTypeTypeManager.\
                get_item_at_index(t_type_idx).nextType
            t_type_idxs.append(t_type_idx)
        # Update dictionary
        u_dict = {"a": 1, "b": 2, "c": 3}
        # Update dictionary with names replaced by IDs
        u_ids_dict = {1: 1, 2: 2, 3: 3}
        self.assertEquals(self.sm.names_to_ids(u_dict, False), u_ids_dict)

        # Part of update dictionary
        u_dict = {"a": 1, "c": 3}
        # Part of update dictionary with names replaced by IDs
        u_ids_dict = {1: 1, 3: 3}
        self.assertEquals(self.sm.names_to_ids(u_dict, False), u_ids_dict)