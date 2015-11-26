import unittest
from mock import MagicMock

from graphene.storage.base import ArrayStore, GeneralTypeStore, \
    GeneralTypeTypeStore, NodeStore, PropertyStore, RelationshipStore, \
    StringStore
from graphene.storage.base.id_store import IdStore
from graphene.storage.defrag.defragmenter import *
from graphene.storage.defrag.reference_map import *


class TestReferenceMap(unittest.TestCase):
    """
    Test that all the references specified in the reference map have correct
    offsets.
    """

    def test_self_ref_update_array(self):
        """
        Simple link of forward references for next and backward refs for prev
        Defragment | 0->1->3 | - | 1->3->5 | - | 3->5->6 | 5->6->0 |
        Result     | 0->[1]->2 | 1->[3]->3 | 2->[5]->4 | 3->[6]->0 |
        """
        a1 = Array(1, True, Property.PropertyType.boolArray, 0, 1, 5, 3, [True])
        a2 = Array(2, True, Property.PropertyType.intArray, 1, 1, 4, 3, [32])
        a3 = Array(3, True, Property.PropertyType.boolArray, 1, 1, 3, 5, [True])
        a4 = Array(4, True, Property.PropertyType.intArray, 3, 1, 2, 5, [24])
        a5 = Array(5, True, Property.PropertyType.charArray, 3, 1, 1, 6, ["a"])
        a6 = Array(6, True, Property.PropertyType.intArray, 5, 1, 3, 0, [14])
        arrays = [a1, a2, a3, a4, a5, a6]
        base_store = ArrayStore()
        for a in arrays:
            base_store.write_item(a)
        delete_idx = [2, 4]
        for i in delete_idx: base_store.delete_item_at_index(i)

        id_store = IdStore(base_store.filename + ".id")
        id_store.get_all_ids = MagicMock(return_value=delete_idx)

        referencing_stores = []

        defragmenter = Defragmenter(base_store, id_store, referencing_stores)
        defragmenter.defragment()
        # Expected values with self references updated
        a1e = Array(1, True, Property.PropertyType.boolArray, 0, 1, 5, 2, [True])
        a3e = Array(2, True, Property.PropertyType.boolArray, 1, 1, 3, 3, [True])
        a5e = Array(3, True, Property.PropertyType.charArray, 2, 1, 1, 4, ["a"])
        a6e = Array(4, True, Property.PropertyType.intArray, 3, 1, 3, 0, [14])
        expected = [a1e, a3e, a5e, a6e]
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, a in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertEqual(val, a, "Defragmented item:\n[%s]\n"
                             "is not equal to expected:\n[%s]" % (val, a))

    def test_ref_update_general_type_type(self):
        """
        Simple link of forward references for next and backward refs for prev
        Defragment | 1->3 | - | 3->5 | - | 5->6 | 6->0 |
        Result     | [1]->2 | [3]->3 | [5]->4 | [6]->0 |
        """
        tt1 = GeneralTypeType(1, True, 1, Property.PropertyType.bool, 3)
        tt2 = GeneralTypeType(2, True, 2, Property.PropertyType.int, 0)
        tt3 = GeneralTypeType(3, True, 3, Property.PropertyType.bool, 5)
        tt4 = GeneralTypeType(4, True, 4, Property.PropertyType.int, 0)
        tt5 = GeneralTypeType(5, True, 5, Property.PropertyType.char, 6)
        tt6 = GeneralTypeType(6, True, 6, Property.PropertyType.int, 0)
        type_types = [tt1, tt2, tt3, tt4, tt5, tt6]
        base_store = GeneralTypeTypeStore("grapheneteststore.generalttstore.db")
        for tt in type_types:
            base_store.write_item(tt)
        delete_idx = [2, 4]
        for i in delete_idx: base_store.delete_item_at_index(i)

        id_store = IdStore(base_store.filename + ".id")
        id_store.get_all_ids = MagicMock(return_value=delete_idx)

        referencing_stores = []
        defragmenter = Defragmenter(base_store, id_store, referencing_stores)
        defragmenter.defragment()
        # Expected values with self references updated
        tt1e = GeneralTypeType(1, True, 1, Property.PropertyType.bool, 2)
        tt3e = GeneralTypeType(2, True, 3, Property.PropertyType.bool, 3)
        tt5e = GeneralTypeType(3, True, 5, Property.PropertyType.char, 4)
        tt6e = GeneralTypeType(4, True, 6, Property.PropertyType.int, 0)
        expected = [tt1e, tt3e, tt5e, tt6e]
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, tt in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertEqual(val, tt, "Defragmented item:\n[%s]\n"
                             "is not equal to expected:\n[%s]" % (val, tt))

    def test_self_ref_update_string(self):
        """
        Simple link of forward references for next and backward refs for prev
        Defragment | 0->1->3 | - | 1->3->5 | - | 3->5->6 | 5->6->0 |
        Result     | 0->[1]->2 | 1->[3]->3 | 2->[5]->4 | 3->[6]->0 |
        """
        s1 = String(1, True, 0, 1, 3, "no")
        s2 = String(2, True, 1, 2, 3, "bored")
        s3 = String(3, True, 1, 3, 5, "who")
        s4 = String(4, True, 3, 4, 5, "bye")
        s5 = String(5, True, 3, 5, 6, "hello")
        s6 = String(6, True, 5, 6, 0, "hi")
        strings = [s1, s2, s3, s4, s5, s6]
        base_store = StringStore("grapheneteststore.string.db")
        for s in strings:
            base_store.write_item(s)
        delete_idx = [2, 4]
        for i in delete_idx: base_store.delete_item_at_index(i)

        id_store = IdStore(base_store.filename + ".id")
        id_store.get_all_ids = MagicMock(return_value=delete_idx)

        referencing_stores = []

        defragmenter = Defragmenter(base_store, id_store, referencing_stores)
        defragmenter.defragment()
        # Expected values with self references updated
        s1e = String(1, True, 0, 1, 2, "no")
        s3e = String(2, True, 1, 3, 3, "who")
        s5e = String(3, True, 2, 5, 4, "hello")
        s6e = String(4, True, 3, 6, 0, "hi")
        expected = [s1e, s3e, s5e, s6e]
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, s in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertEqual(val, s, "Defragmented item:\n[%s]\n"
                             "is not equal to expected:\n[%s]" % (val, s))

    def test_self_ref_update_relationship(self):
        """
        Simple link of forward references for next and backward refs for prev
        Defragment |0,0->1->3,5| - |1,5->3->5,6| - |3,1->5->6,0|1,5->6->0,3|
        Result     |0,0->[1]->2,3|1,3->[3]->3,4|2,1->[5]->4,0|1,3->[6]->0,2|
        """
        r1 = Relationship(1, True, Relationship.Direction.left,
                          1, 2, 1, 0, 3, 0, 5, 6)
        r2 = Relationship(2, True, Relationship.Direction.right,
                          3, 4, 2, 0, 3, 0, 5, 6)
        r3 = Relationship(3, True, Relationship.Direction.left,
                          5, 6, 3, 1, 5, 5, 6, 10)
        r4 = Relationship(4, True, Relationship.Direction.right,
                          7, 8, 4, 3, 6, 1, 0, 14)
        r5 = Relationship(5, True, Relationship.Direction.left,
                          9, 10, 5, 3, 6, 1, 0, 14)
        r6 = Relationship(6, True, Relationship.Direction.right,
                          11, 12, 6, 1, 0, 5, 3, 20)
        relationships = [r1, r2, r3, r4, r5, r6]
        base_store = RelationshipStore()
        for r in relationships:
            base_store.write_item(r)
        delete_idx = [2, 4]
        for i in delete_idx: base_store.delete_item_at_index(i)

        id_store = IdStore(base_store.filename + ".id")
        id_store.get_all_ids = MagicMock(return_value=delete_idx)

        referencing_stores = []
        defragmenter = Defragmenter(base_store, id_store, referencing_stores)
        defragmenter.defragment()
        # Expected values with self references updated
        r1e = Relationship(1, True, Relationship.Direction.left,
                           1, 2, 1, 0, 2, 0, 3, 6)
        r3e = Relationship(2, True, Relationship.Direction.left,
                           5, 6, 3, 1, 3, 3, 4, 10)
        r5e = Relationship(3, True, Relationship.Direction.left,
                           9, 10, 5, 2, 4, 1, 0, 14)
        r6e = Relationship(4, True, Relationship.Direction.right,
                           11, 12, 6, 1, 0, 3, 2, 20)
        expected = [r1e, r3e, r5e, r6e]
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, r in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertEqual(val, r, "Defragmented item:\n[%s]\n"
                             "is not equal to expected:\n[%s]" % (val, r))

    def test_self_ref_update_property(self):
        """
        Simple link of forward references for next and backward refs for prev
        Defragment | 0->1->3 | - | 1->3->5 | - | 3->5->6 | 5->6->0 |
        Result     | 0->[1]->2 | 1->[3]->3 | 2->[5]->4 | 3->[6]->0 |
        """
        p1 = Property(1, True, Property.PropertyType.bool, 9, 0, 3, False)
        p2 = Property(2, True, Property.PropertyType.int, 8, 1, 3, 32)
        p3 = Property(3, True, Property.PropertyType.bool, 7, 1, 5, True)
        p4 = Property(4, True, Property.PropertyType.int, 6, 3, 5, 24)
        p5 = Property(5, True, Property.PropertyType.char, 5, 3, 6, "a")
        p6 = Property(6, True, Property.PropertyType.int, 4, 5, 0, 32)
        properties = [p1, p2, p3, p4, p5, p6]
        base_store = PropertyStore()
        for p in properties:
            base_store.write_item(p)
        delete_idx = [2, 4]
        for i in delete_idx: base_store.delete_item_at_index(i)

        id_store = IdStore(base_store.filename + ".id")
        id_store.get_all_ids = MagicMock(return_value=delete_idx)

        referencing_stores = []
        defragmenter = Defragmenter(base_store, id_store, referencing_stores)
        defragmenter.defragment()
        # Expected values with self references updated
        p1e = Property(1, True, Property.PropertyType.bool, 9, 0, 2, False)
        p3e = Property(2, True, Property.PropertyType.bool, 7, 1, 3, True)
        p5e = Property(3, True, Property.PropertyType.char, 5, 2, 4, "a")
        p6e = Property(4, True, Property.PropertyType.int, 4, 3, 0, 32)
        expected = [p1e, p3e, p5e, p6e]
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, p in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertEqual(val, p, "Defragmented item:\n[%s]\n"
                             "is not equal to expected:\n[%s]" % (val, p))
