import unittest

from graphene.errors.storage_manager_errors import *
from graphene.errors.query_errors import NonexistentPropertyException
from graphene.storage import (StorageManager, GrapheneStore, Property,
                              Relationship, Node)
from graphene.storage.intermediate.node_property import NodeProperty
from graphene.storage.intermediate.relation_property import RelationProperty
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
        self.sm.close()

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
                read_string_at_index(tt.typeName)
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
        type_name = self.sm.nodeTypeNameManager.read_string_at_index(t.nameId)
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

        self.assertEquals(self.sm.nodeTypeNameManager.read_string_at_index(
            t1.nameId), "T")
        self.assertEquals(self.sm.nodeTypeNameManager.read_string_at_index(
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
        self.assertIsNoneOrEOF(self.sm.prop_string_manager.read_string_at_index(rp2[1].propBlockId))
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
        self.assertIsNoneOrEOF(self.sm.prop_string_manager.read_string_at_index(rp3[1].propBlockId))
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
        self.assertIsNoneOrEOF(self.sm.prop_string_manager.read_string_at_index(rp1[1].propBlockId))
        self.assertIsNoneOrEOF(self.sm.array_manager.read_array_at_index(rp1[2].propBlockId))

        self.assertEqual(n1.relId, 0)
        self.assertEqual(n2.relId, 0)

    def test_update_items_simple(self, node_flag=True):
        """
        Test that updating an item's properties works properly, in a 1 property
        case. [General Test]

        :param node_flag: Set to false to test update for relations
        :type node_flag: bool
        :return: Nothing
        :rtype: None
        """
        if node_flag:
            update = self.sm.update_nodes
            itemprop = NodeProperty
            itemprop_store = self.sm.nodeprop
        else:
            update = self.sm.update_relations
            itemprop = RelationProperty
            itemprop_store = self.sm.relprop

        # Create type T with schema tuple for properties
        type_name = "T"
        schema_tup = (("a", "int"),)
        t = self.sm.create_node_type(type_name, schema_tup)
        # Create 3 nodes of type T
        prop_tup1 = ((Property.PropertyType.int, 2),)
        prop_tup2 = ((Property.PropertyType.int, 3),)
        prop_tup3 = ((Property.PropertyType.int, 5),)
        i1, p1 = self.sm.insert_node(t, prop_tup1)
        i2, p2 = self.sm.insert_node(t, prop_tup2)
        i3, p3 = self.sm.insert_node(t, prop_tup3)

        # If testing relations, make the properties for relations
        if not node_flag:
            type_name = "R"
            t = self.sm.create_relationship_type(type_name, schema_tup)
            # Save nodes since items will be overwritten for generality
            n1, n2, n3 = (i1, i2, i3)
            r1i = self.sm.insert_relation(t, prop_tup1, n1, n2).index
            r2i = self.sm.insert_relation(t, prop_tup2, n2, n3).index
            r3i = self.sm.insert_relation(t, prop_tup3, n3, n1).index
            # Overwrite items
            i1, p1 = self.sm.relprop[r1i]
            i2, p2 = self.sm.relprop[r2i]
            i3, p3 = self.sm.relprop[r3i]

        # Update items 1 and 3 with value 10, since "a" is the first property,
        # set the update key accordingly
        updates = {0: 10}
        # Create itemprops for update items
        itemprop1 = itemprop(i1, p1, t, type_name)
        itemprop3 = itemprop(i3, p3, t, type_name)
        itemprops = [itemprop1, itemprop3]

        update(itemprops, updates)
        # Check that values are updated
        i1_f, p1_f = itemprop_store[i1.index]
        i2_f, p2_f = itemprop_store[i2.index]
        i3_f, p3_f = itemprop_store[i3.index]

        self.assertTrue(self.valid_update(self.sm, p1_f, updates))
        self.assertTrue(self.valid_update(self.sm, p3_f, updates))
        # Check that untouched values are the same
        self.assertTrue(self.equal_properties(p2, p2_f))

    def test_update_items_complex(self, node_flag=True):
        """
        Test that updating an item's properties works properly, in a 4 property
        case. [General Test]

        :param node_flag: Set to false to test update for relations
        :type node_flag: bool
        :return: Nothing
        :rtype: None
        """
        if node_flag:
            update = self.sm.update_nodes
            itemprop = NodeProperty
            itemprop_store = self.sm.nodeprop
        else:
            update = self.sm.update_relations
            itemprop = RelationProperty
            itemprop_store = self.sm.relprop

        # Create type T with schema tuple for properties
        schema_tup = (("a", "int"), ("b", "float"),
                      ("c", "char"), ("d", "double"))
        type_name = "T"
        t = self.sm.create_node_type(type_name, schema_tup)

        # Create 4 nodes of type T
        prop_tup1 = ((Property.PropertyType.int, 2),
                     (Property.PropertyType.float, 3.4),
                     (Property.PropertyType.char, "a"),
                     (Property.PropertyType.double, 5e-9))
        prop_tup2 = ((Property.PropertyType.int, 5),
                     (Property.PropertyType.float, 123.4),
                     (Property.PropertyType.char, "b"),
                     (Property.PropertyType.double, 5e-8))
        prop_tup3 = ((Property.PropertyType.int, 254321),
                     (Property.PropertyType.float, 9.4),
                     (Property.PropertyType.char, "c"),
                     (Property.PropertyType.double, 5e-4))
        prop_tup4 = ((Property.PropertyType.int, 32),
                     (Property.PropertyType.float, 9.4),
                     (Property.PropertyType.char, "c"),
                     (Property.PropertyType.double, 5e-4))
        i1, p1 = self.sm.insert_node(t, prop_tup1)
        i2, p2 = self.sm.insert_node(t, prop_tup2)
        i3, p3 = self.sm.insert_node(t, prop_tup3)
        i4, p4 = self.sm.insert_node(t, prop_tup4)

        # If testing relations, make the properties for relations
        if not node_flag:
            type_name = "R"
            t = self.sm.create_relationship_type(type_name, schema_tup)
            # Save nodes since items will be overwritten for generality
            n1, n2, n3, n4 = (i1, i2, i3, i4)
            r1i = self.sm.insert_relation(t, prop_tup1, n1, n2).index
            r2i = self.sm.insert_relation(t, prop_tup2, n2, n3).index
            r3i = self.sm.insert_relation(t, prop_tup3, n3, n1).index
            r4i = self.sm.insert_relation(t, prop_tup4, n4, n1).index
            # Overwrite items
            i1, p1 = self.sm.relprop[r1i]
            i2, p2 = self.sm.relprop[r2i]
            i3, p3 = self.sm.relprop[r3i]
            i4, p4 = self.sm.relprop[r4i]

        # Update items 1 and 3 with new values, set the update keys accordingly
        updates = {1: 2.1, 2: "f", 3: 4e-200}
        # Create itemprops for update items
        itemprop1 = itemprop(i1, p1, t, type_name)
        itemprop3 = itemprop(i3, p3, t, type_name)
        itemprops = [itemprop1, itemprop3]
        # Perform update
        update(itemprops, updates)

        # Check that values are updated
        i1_f, p1_f = itemprop_store[i1.index]
        i2_f, p2_f = itemprop_store[i2.index]
        i3_f, p3_f = itemprop_store[i3.index]
        i4_f, p4_f = itemprop_store[i4.index]

        self.assertTrue(self.valid_update(self.sm, p1_f, updates))
        self.assertTrue(self.valid_update(self.sm, p3_f, updates))
        # Check that untouched values are the same
        self.assertTrue(self.equal_properties(p2, p2_f))
        self.assertTrue(self.equal_properties(p4, p4_f))

    def test_update_items_string(self, node_flag=True):
        """
        Test that updating a node's properties works properly, when
        updating strings. [General Test]

        :param node_flag: Set to false to test update for relations
        :type node_flag: bool
        :return: Nothing
        :rtype: None
        """
        if node_flag:
            update = self.sm.update_nodes
            itemprop = NodeProperty
            itemprop_store = self.sm.nodeprop
        else:
            update = self.sm.update_relations
            itemprop = RelationProperty
            itemprop_store = self.sm.relprop

        # Create type T with schema tuple for properties
        schema_tup = (("a", "int"), ("b", "string"),
                      ("c", "char"), ("d", "string"))
        type_name = "T"
        t = self.sm.create_node_type(type_name, schema_tup)

        # Property tuples
        prop_tup1 = ((Property.PropertyType.int, 2),
                     (Property.PropertyType.string, 99*"a"),
                     (Property.PropertyType.char, "w"),
                     (Property.PropertyType.string, "b"))
        prop_tup2 = ((Property.PropertyType.int, 1020),
                     (Property.PropertyType.string, 6*"c"),
                     (Property.PropertyType.char, "x"),
                     (Property.PropertyType.string, 92*"d"))
        prop_tup3 = ((Property.PropertyType.int, 21),
                     (Property.PropertyType.string, 9*"e"),
                     (Property.PropertyType.char, "y"),
                     (Property.PropertyType.string, 122*"f"))
        prop_tup4 = ((Property.PropertyType.int, 2432),
                     (Property.PropertyType.string, 2*"g"),
                     (Property.PropertyType.char, "z"),
                     (Property.PropertyType.string, 40*"h"))

        # Create 4 nodes of type T
        i1, p1 = self.sm.insert_node(t, prop_tup1)
        i2, p2 = self.sm.insert_node(t, prop_tup2)
        i3, p3 = self.sm.insert_node(t, prop_tup3)
        i4, p4 = self.sm.insert_node(t, prop_tup4)

        # If testing relations, make the properties for relations
        if not node_flag:
            type_name = "R"
            t = self.sm.create_relationship_type(type_name, schema_tup)
            # Save nodes since items will be overwritten for generality
            n1, n2, n3, n4 = (i1, i2, i3, i4)
            r1i = self.sm.insert_relation(t, prop_tup1, n1, n2).index
            r2i = self.sm.insert_relation(t, prop_tup2, n2, n3).index
            r3i = self.sm.insert_relation(t, prop_tup3, n3, n1).index
            r4i = self.sm.insert_relation(t, prop_tup4, n4, n1).index
            # Overwrite items
            i1, p1 = self.sm.relprop[r1i]
            i2, p2 = self.sm.relprop[r2i]
            i3, p3 = self.sm.relprop[r3i]
            i4, p4 = self.sm.relprop[r4i]

        # Update items 2, 3, 4 with new values, set the update keys accordingly
        updates = {0: 2, 1: "", 3: 102*"j"}
        # Create itemprops for update items
        itemprop2 = itemprop(i2, p2, t, type_name)
        itemprop3 = itemprop(i3, p3, t, type_name)
        itemprop4 = itemprop(i4, p4, t, type_name)
        itemprops = [itemprop3, itemprop4, itemprop2]

        update(itemprops, updates)
        # Check that values are updated
        i1_f, p1_f = itemprop_store[i1.index]
        i2_f, p2_f = itemprop_store[i2.index]
        i3_f, p3_f = itemprop_store[i3.index]
        i4_f, p4_f = itemprop_store[i4.index]

        self.assertTrue(self.valid_update(self.sm, p2_f, updates))
        self.assertTrue(self.valid_update(self.sm, p3_f, updates))
        self.assertTrue(self.valid_update(self.sm, p4_f, updates))
        # Check that untouched values are the same
        self.assertTrue(self.equal_properties(p1, p1_f))

    def test_update_items_array(self, node_flag=True):
        """
        Test that updating a node's properties works properly, when updating
        arrays. String arrays tested separately. [General Test]

        :param node_flag: Set to false to test update for relations
        :type node_flag: bool
        :return: Nothing
        :rtype: None
        """
        if node_flag:
            update = self.sm.update_nodes
            itemprop = NodeProperty
            itemprop_store = self.sm.nodeprop
        else:
            update = self.sm.update_relations
            itemprop = RelationProperty
            itemprop_store = self.sm.relprop

        # Create type T with schema tuple for properties
        type_name = "T"
        schema_tup = (("a", "int[]"), ("b", "string"),
                    ("c", "char[]"), ("d", "string"))
        t = self.sm.create_node_type(type_name, schema_tup)

        # Property tuples
        prop_tup1 = ((Property.PropertyType.intArray, 80 * [243]),
                     (Property.PropertyType.string, 99*"a"),
                     (Property.PropertyType.charArray, 43 * ["w"]),
                     (Property.PropertyType.string, "b"))
        prop_tup2 = ((Property.PropertyType.intArray, 56 * [1020]),
                     (Property.PropertyType.string, 6*"c"),
                     (Property.PropertyType.charArray, ["x"]),
                     (Property.PropertyType.string, 92*"d"))
        prop_tup3 = ((Property.PropertyType.intArray, [21]),
                     (Property.PropertyType.string, 9*"e"),
                     (Property.PropertyType.charArray, 80 * ["y"]),
                     (Property.PropertyType.string, 122*"f"))
        prop_tup4 = ((Property.PropertyType.intArray, 102 * [2432]),
                     (Property.PropertyType.string, 2*"g"),
                     (Property.PropertyType.charArray, 32 * ["z"]),
                     (Property.PropertyType.string, 40*"h"))

        # Create 4 nodes of type T
        i1, p1 = self.sm.insert_node(t, prop_tup1)
        i2, p2 = self.sm.insert_node(t, prop_tup2)
        i3, p3 = self.sm.insert_node(t, prop_tup3)
        i4, p4 = self.sm.insert_node(t, prop_tup4)

        # If testing relations, make the properties for relations
        if not node_flag:
            type_name = "R"
            t = self.sm.create_relationship_type(type_name, schema_tup)
            # Save nodes since items will be overwritten for generality
            n1, n2, n3, n4 = (i1, i2, i3, i4)
            r1i = self.sm.insert_relation(t, prop_tup1, n1, n2).index
            r2i = self.sm.insert_relation(t, prop_tup2, n2, n3).index
            r3i = self.sm.insert_relation(t, prop_tup3, n3, n1).index
            r4i = self.sm.insert_relation(t, prop_tup4, n4, n1).index
            # Overwrite items
            i1, p1 = self.sm.relprop[r1i]
            i2, p2 = self.sm.relprop[r2i]
            i3, p3 = self.sm.relprop[r3i]
            i4, p4 = self.sm.relprop[r4i]

        # Update items 2 and 4 with new values, set the update keys accordingly
        updates = {0: [], 1: 5 * "i", 2: 43 * ["j"]}
        # Create itemprops for update items
        itemprop2 = itemprop(i2, p2, t, type_name)
        itemprop4 = itemprop(i4, p4, t, type_name)
        itemprops = [itemprop4, itemprop2]

        update(itemprops, updates)

        # Check that values are updated
        i1_f, p1_f = itemprop_store[i1.index]
        i2_f, p2_f = itemprop_store[i2.index]
        i3_f, p3_f = itemprop_store[i3.index]
        i4_f, p4_f = itemprop_store[i4.index]

        self.assertTrue(self.valid_update(self.sm, p2_f, updates))
        self.assertTrue(self.valid_update(self.sm, p4_f, updates))
        # Check that untouched values are the same
        self.assertTrue(self.equal_properties(p1, p1_f))
        self.assertTrue(self.equal_properties(p3, p3_f))

    def test_update_items_string_array(self, node_flag=True):
        """
        Test that updating a node's properties works properly, when updating
        string arrays. [General Test]

        :param node_flag: Set to false to test update for relations
        :type node_flag: bool
        :return: Nothing
        :rtype: None
        """

        if node_flag:
            update = self.sm.update_nodes
            itemprop = NodeProperty
            itemprop_store = self.sm.nodeprop
        else:
            update = self.sm.update_relations
            itemprop = RelationProperty
            itemprop_store = self.sm.relprop

        # Create type T with schema tuple for properties
        type_name = "T"
        schema_tup = (("a", "int[]"), ("b", "string[]"),
                      ("c", "char[]"), ("d", "string[]"))
        t = self.sm.create_node_type(type_name, schema_tup)

        # Property tuples
        prop_tup1 = ((Property.PropertyType.intArray, 80 * [243]),
                     (Property.PropertyType.stringArray, 9*[42 * "a"]),
                     (Property.PropertyType.charArray, 43 * ["w"]),
                     (Property.PropertyType.stringArray, 62 * ["b"]),)
        prop_tup2 = ((Property.PropertyType.intArray, 56 * [1020]),
                     (Property.PropertyType.stringArray, [42 * "c"]),
                     (Property.PropertyType.charArray, ["x"]),
                     (Property.PropertyType.stringArray, 92 * ["d"]),)
        prop_tup3 = ((Property.PropertyType.intArray, [21]),
                     (Property.PropertyType.stringArray, 9 * [8 * "e"]),
                     (Property.PropertyType.charArray, 80 * ["y"]),
                     (Property.PropertyType.stringArray, 122 * [98 * "f"]),)
        prop_tup4 = ((Property.PropertyType.intArray, 102 * [2432]),
                     (Property.PropertyType.stringArray, 82 * [42 * "g"]),
                     (Property.PropertyType.charArray, 32 * ["z"]),
                     (Property.PropertyType.stringArray, 40 * [32 * "h"]),)

        # Create 4 nodes of type T
        i1, p1 = self.sm.insert_node(t, prop_tup1)
        i2, p2 = self.sm.insert_node(t, prop_tup2)
        i3, p3 = self.sm.insert_node(t, prop_tup3)
        i4, p4 = self.sm.insert_node(t, prop_tup4)

        # If testing relations, make the properties for relations
        if not node_flag:
            type_name = "R"
            t = self.sm.create_relationship_type(type_name, schema_tup)
            # Save nodes since items will be overwritten for generality
            n1, n2, n3, n4 = (i1, i2, i3, i4)
            r1i = self.sm.insert_relation(t, prop_tup1, n1, n2).index
            r2i = self.sm.insert_relation(t, prop_tup2, n2, n3).index
            r3i = self.sm.insert_relation(t, prop_tup3, n3, n1).index
            r4i = self.sm.insert_relation(t, prop_tup4, n4, n1).index
            # Overwrite items
            i1, p1 = self.sm.relprop[r1i]
            i2, p2 = self.sm.relprop[r2i]
            i3, p3 = self.sm.relprop[r3i]
            i4, p4 = self.sm.relprop[r4i]

        # Update items 2 and 3 with new values, set the update keys accordingly
        updates = {0: 82 * [2431], 1: [], 3: 43 * [68 * "j"]}
        # Create itemprops for update items
        itemprop2 = itemprop(i2, p2, t, type_name)
        itemprop3 = itemprop(i3, p3, t, type_name)
        itemprops = [itemprop3, itemprop2]

        # Perform update
        update(itemprops, updates)

        # Check that values are updated
        n1_f, p1_f = itemprop_store[i1.index]
        n2_f, p2_f = itemprop_store[i2.index]
        n3_f, p3_f = itemprop_store[i3.index]
        n4_f, p4_f = itemprop_store[i4.index]

        self.assertTrue(self.valid_update(self.sm, p2_f, updates))
        self.assertTrue(self.valid_update(self.sm, p3_f, updates))
        # Check that untouched values are the same
        self.assertTrue(self.equal_properties(p1, p1_f))
        self.assertTrue(self.equal_properties(p4, p4_f))

    def test_update_relations_simple(self):
        """
        Test updating relation properties in a simple case with primitives
        """
        self.test_update_items_simple(False)

    def test_update_relations_complex(self):
        """
        Test updating relation properties in a complex case with primitives
        """
        self.test_update_items_complex(False)

    def test_update_relations_string(self):
        """
        Test updating relation properties in a case with strings
        """
        self.test_update_items_string(False)

    def test_update_relations_array(self):
        """
        Test updating relation properties in a case with arrays
        """
        self.test_update_items_array(False)

    def test_update_relations_string_array(self):
        """
        Test updating relation properties in a case with string arrays
        """
        self.test_update_items_string_array(False)

    def valid_update(self, storage_manager, properties, updates):
        """
        Test that the given properties have the corresponding update values
        changed.

        :param storage_manager: Storage manager to use to check strings & arrays
        :type storage_manager: StorageManager
        :param properties: List of properties to check
        :type properties: list[Properties]
        :param updates: Dictionary with indexes of properties and new values
        :type updates: dict[int: Any]
        :return: Whether the properties have the given update values changed
        :rtype: bool
        """
        string_manager = storage_manager.prop_string_manager
        array_manager = storage_manager.array_manager

        for index, new_val in updates.iteritems():
            prop = properties[index]
            cur_val = prop.propBlockId
            if prop.is_string():
                if string_manager.read_string_at_index(cur_val) != new_val:
                    return False
            elif prop.is_array():
                if array_manager.read_array_at_index(cur_val) != new_val:
                    return False
            # Primitive, just check values
            elif cur_val != new_val:
                return False
        return True

    def equal_properties(self, props1, props2):
        """
        Check that the two given list of properties are equal.

        :param props1: First property list
        :type props1: list[Property]
        :param props2: Second property list
        :type props2: list[Property]
        :return: Whether the two lists have equal property values
        :rtype: bool
        """
        for index, prop1 in enumerate(props1):
            prop2 = props2[index]
            val1 = prop1.propBlockId
            val2 = prop2.propBlockId

            if prop1.is_string():
                if not prop2.is_string():
                    return False
            elif prop1.is_array():
                if not prop2.is_array():
                    return False
            # Both arrays and primitives must have the same value, if arrays or
            # strings have the same ID value, then they are obviously the same
            if val1 != val2:
                return False
        return True

    # --- Alter command tests --- #
    def properties_attached(self, propIdLeft, propIdRight):
        self.assertEqual(self.sm.property_manager.get_item_at_index(propIdLeft).nextPropId, propIdRight)
        self.assertEqual(self.sm.property_manager.get_item_at_index(propIdRight).prevPropId, propIdLeft)

    def property_is_first(self, itemId, propId, node_flag):
        if node_flag:
            item_manager = self.sm.node_manager
        else:
            item_manager = self.sm.relationship_manager
        self.assertEqual(item_manager.get_item_at_index(itemId).propId, propId)
        self.assertEqual(self.sm.property_manager.get_item_at_index(propId).prevPropId, 0)

    def drop_property_three_items_five_props(self, name, (i1, p1), (i2, p2), (i3, p3), node_flag):
        i1i, p1i = i1.index, map(lambda p: p.index, p1)
        i2i, p2i = i2.index, map(lambda p: p.index, p2)
        i3i, p3i = i3.index, map(lambda p: p.index, p3)

        with self.assertRaises(NonexistentPropertyException):
            self.sm.drop_property(name, "foo", node_flag)

        self.sm.drop_property(name, "c", node_flag)

        self.assertIsNoneOrEOF(self.sm.property_manager.get_item_at_index(p1i[2]))
        self.assertIsNoneOrEOF(self.sm.property_manager.get_item_at_index(p2i[2]))
        self.assertIsNoneOrEOF(self.sm.property_manager.get_item_at_index(p3i[2]))

        self.properties_attached(p1i[1], p1i[3])
        self.properties_attached(p2i[1], p2i[3])
        self.properties_attached(p3i[1], p3i[3])

        self.sm.drop_property(name, "a", node_flag)

        self.assertIsNoneOrEOF(self.sm.property_manager.get_item_at_index(p1i[0]))
        self.assertIsNoneOrEOF(self.sm.property_manager.get_item_at_index(p2i[0]))
        self.assertIsNoneOrEOF(self.sm.property_manager.get_item_at_index(p3i[0]))

        self.property_is_first(i1i, p1i[1], node_flag)
        self.property_is_first(i2i, p2i[1], node_flag)
        self.property_is_first(i3i, p3i[1], node_flag)

        self.sm.drop_property(name, "e", node_flag)

        self.assertIsNoneOrEOF(self.sm.property_manager.get_item_at_index(p1i[4]))
        self.assertIsNoneOrEOF(self.sm.property_manager.get_item_at_index(p2i[4]))
        self.assertIsNoneOrEOF(self.sm.property_manager.get_item_at_index(p3i[4]))

        self.assertEqual(self.sm.property_manager.get_item_at_index(p1i[3]).nextPropId, 0)
        self.assertEqual(self.sm.property_manager.get_item_at_index(p2i[3]).nextPropId, 0)
        self.assertEqual(self.sm.property_manager.get_item_at_index(p3i[3]).nextPropId, 0)


    def test_drop_property(self):
        schema = ( ("a", "string"), ("b", "int"), ("c", "int[]"), ("d", "bool"), ("e", "string[]") )
        types = (Property.PropertyType.string, Property.PropertyType.int,
                 Property.PropertyType.intArray, Property.PropertyType.bool,
                 Property.PropertyType.stringArray)
        data1 = zip(types, ("foo", 1, [1,2], False, ["bar"]))
        data2 = zip(types, ("bat", 8, [3], True, []))
        data3 = zip(types, ("yar", 3, [], True, ["baz", "qux"]))

        t = self.sm.create_node_type("T", schema)
        n1, p1 = self.sm.insert_node(t, data1)
        n2, p2 = self.sm.insert_node(t, data2)
        n3, p3 = self.sm.insert_node(t, data3)

        self.drop_property_three_items_five_props("T", (n1, p1), (n2, p2), (n3, p3), True)

        r = self.sm.create_relationship_type("R", schema)
        r1 = self.sm.insert_relation(r, data1, n1, n2)
        p1 = self.sm.relprop[r1.index][1]
        r2 = self.sm.insert_relation(r, data2, n1, n3)
        p2 = self.sm.relprop[r2.index][1]
        r3 = self.sm.insert_relation(r, data3, n2, n3)
        p3 = self.sm.relprop[r3.index][1]

        self.drop_property_three_items_five_props("R", (r1, p1), (r2, p2), (r3, p3), False)

    def add_property_three_items(self, name, (i1, p1), (i2, p2), (i3, p3), node_flag):
        if node_flag:
            item_manager = self.sm.node_manager
            get_item = self.sm.get_node
        else:
            item_manager = self.sm.relationship_manager
            get_item = self.sm.get_relation

        i1i, p1i = i1.index, map(lambda p: p.index, p1)
        i2i, p2i = i2.index, map(lambda p: p.index, p2)
        i3i, p3i = i3.index, map(lambda p: p.index, p3)

        i1props = map(lambda i: self.sm.get_property_value(
                                self.sm.property_manager.get_item_at_index(i)),
                      p1i)
        i2props = map(lambda i: self.sm.get_property_value(
                                self.sm.property_manager.get_item_at_index(i)),
                      p2i)
        i3props = map(lambda i: self.sm.get_property_value(
                                self.sm.property_manager.get_item_at_index(i)),
                      p3i)

        props_to_add = (
            ("b", "int", Property.PropertyType.int, Property.DefaultValue.int),
            ("c", "float", Property.PropertyType.float, Property.DefaultValue.float),
            ("d", "string", Property.PropertyType.string, Property.DefaultValue.string),
            ("e", "bool", Property.PropertyType.bool, Property.DefaultValue.bool),
            ("f", "int[]", Property.PropertyType.intArray, Property.DefaultValue.intArray),
        )

        for prop_name, prop_type, prop_tt_type, default_val in props_to_add:
            i1props.append(default_val)
            i2props.append(default_val)
            i3props.append(default_val)

            new_tt = self.sm.add_property(name, prop_name, prop_type, node_flag)

            self.assertEqual(new_tt.propertyType, prop_tt_type)

            self.assertListEqual(get_item(i1i).properties, i1props)
            self.assertListEqual(get_item(i2i).properties, i2props)
            self.assertListEqual(get_item(i3i).properties, i3props)

    def test_add_property(self):
        schema = ( ("a", "string"), )
        types = (Property.PropertyType.string,)
        data1 = zip(types, ("a",))
        data2 = zip(types, ("b",))
        data3 = zip(types, ("c",))

        t = self.sm.create_node_type("T", schema)
        n1, p1 = self.sm.insert_node(t, data1)
        n2, p2 = self.sm.insert_node(t, data2)
        n3, p3 = self.sm.insert_node(t, data3)
        self.add_property_three_items("T", (n1, p1), (n2, p2), (n3, p3), True)

        r = self.sm.create_relationship_type("R", ())
        r1 = self.sm.insert_relation(r, (), n1, n2)
        p1 = self.sm.relprop[r1.index][1]
        r2 = self.sm.insert_relation(r, (), n1, n3)
        p2 = self.sm.relprop[r2.index][1]
        r3 = self.sm.insert_relation(r, (), n2, n3)
        p3 = self.sm.relprop[r3.index][1]
        self.add_property_three_items("R", (r1, p1), (r2, p2), (r3, p3), False)

    def change_property_item(self, name, (i, p), node_flag):
        if node_flag:
            item_manager = self.sm.node_manager
            get_item = self.sm.get_node
        else:
            item_manager = self.sm.relationship_manager
            get_item = self.sm.get_relation

        with self.assertRaises(NonexistentPropertyException):
            self.sm.change_property(name, "q", "float", node_flag)

        self.sm.change_property(name, "a", "float", node_flag)

        new_value = get_item(i.index).properties[1]
        self.assertEqual(type(new_value), float)
        self.assertEqual(new_value, 1.0)

        self.sm.change_property(name, "a", "float[]", node_flag)

        new_value = get_item(i.index).properties[1]
        self.assertEqual(type(new_value), list)
        self.assertEqual(type(new_value[0]), float)
        self.assertEqual(new_value, [1.0])

        self.sm.change_property(name, "a", "int[]", node_flag)

        new_value = get_item(i.index).properties[1]
        self.assertEqual(type(new_value), list)
        self.assertEqual(type(new_value[0]), int)
        self.assertEqual(new_value, [1])

        self.sm.change_property(name, "a", "float", node_flag)

        new_value = get_item(i.index).properties[1]
        self.assertEqual(type(new_value), float)
        self.assertEqual(new_value, 0.0)

        self.sm.change_property(name, "a", "string", node_flag)

        new_value = get_item(i.index).properties[1]
        self.assertEqual(type(new_value), unicode)
        self.assertEqual(new_value, "")

        self.sm.change_property(name, "c", "string", node_flag)

        new_value = get_item(i.index).properties[0]
        self.assertEqual(type(new_value), unicode)
        self.assertEqual(new_value, "a")

    def test_change_property(self):
        schema = ( ("c", "string"), ("a", "int"), )
        types = (Property.PropertyType.string, Property.PropertyType.int,)
        data = zip(types, ("a", 1,))
        data2 = zip(types, ("b", 2,))

        t = self.sm.create_node_type("T", schema)
        n, p = self.sm.insert_node(t, data)
        n2, p2 = self.sm.insert_node(t, data2)

        self.change_property_item("T", (n, p), True)

        rt = self.sm.create_relationship_type("R", schema)
        r = self.sm.insert_relation(rt, data, n, n2)
        rp = self.sm.relprop[r.index][1]

        self.change_property_item("R", (r, rp), False)

    def rename_property_helper(self, name, node_flag):
        _, type_schema = self.sm.get_type_data(name, node_flag)
        self.assertEqual(type_schema[0][1], "a")

        self.sm.rename_property(name, "a", "b", node_flag)

        _, type_schema = self.sm.get_type_data(name, node_flag)
        self.assertEqual(type_schema[0][1], "b")

        with self.assertRaises(NonexistentPropertyException):
            self.sm.rename_property(name, "a", "b", node_flag)

    def test_rename_property(self):
        schema = ( ("a", "string"), )
        types = (Property.PropertyType.string,)

        t = self.sm.create_node_type("T", schema)
        self.rename_property_helper("T", True)

        r = self.sm.create_relationship_type("R", schema)
        self.rename_property_helper("R", False)

    # --- Helpers --- #
    def test_is_convertible(self):
        numerical_types = [
            Property.PropertyType.int,
            Property.PropertyType.long,
            Property.PropertyType.short,
            Property.PropertyType.float,
            Property.PropertyType.double
        ]
        numerical_arrays = map(lambda t: Property.PropertyType.get_array_type(t),
                               numerical_types)
        for t in numerical_types:
            for s in numerical_types:
                # All numerical types are OK to convert amongst each other
                self.assertTrue(self.sm.is_convertible(t, s))
            for s in numerical_arrays:
                # All numerical types are OK to convert to an array of any other
                # numerical type
                self.assertTrue(self.sm.is_convertible(t, s))
            # Can convert from bool to number, but not from string or char to
            # number
            self.assertTrue(self.sm.is_convertible(Property.PropertyType.bool, t))
            self.assertFalse(self.sm.is_convertible(Property.PropertyType.char, t))
            self.assertFalse(self.sm.is_convertible(Property.PropertyType.string, t))

        # Can't convert from array to any non-array value
        for t in Property.PropertyType:
            if not Property.PropertyType.is_array(t):
                continue
            for s in Property.PropertyType:
                if Property.PropertyType.is_array(t):
                    continue
                self.assertFalse(self.sm.is_convertible(t, s), "%s %s" % (t, s))
