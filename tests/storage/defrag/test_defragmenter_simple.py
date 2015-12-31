import unittest
from mock import MagicMock

from graphene.storage.base.graphene_store import GrapheneStore
from graphene.storage.base.id_store import IdStore
from graphene.storage.base.property_store import PropertyStore, Property
from graphene.storage.defrag.defragmenter import *


class TestDefragmenterSimple(unittest.TestCase):
    def setUp(self):
        """
        Set up the GrapheneStore so that it writes datafiles to the testing
        directory
        """
        GrapheneStore.TESTING = True

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_simple_defragment1(self):
        """
        Defragment | 1 | 2 | 3 | 4 | 5 | 6 |
        Result     | 1 | 2 | 3 | 4 | 5 | 6 |
        """
        p1 = Property(1, True, Property.PropertyType.bool, 9, 0, 0, False)
        p2 = Property(2, True, Property.PropertyType.int, 8, 0, 0, 32)
        p3 = Property(3, True, Property.PropertyType.bool, 7, 0, 0, True)
        p4 = Property(4, True, Property.PropertyType.int, 6, 0, 0, 24)
        p5 = Property(5, True, Property.PropertyType.char, 5, 0, 0, "a")
        p6 = Property(6, True, Property.PropertyType.int, 4, 0, 0, 32)
        properties = [p1, p2, p3, p4, p5, p6]
        base_store = PropertyStore()
        for p in properties:
            base_store.write_item(p)

        id_store = IdStore(base_store.filename + ".id")
        id_store.get_all_ids = MagicMock(return_value=[])

        referencing_stores = []

        defragmenter = Defragmenter(base_store, id_store, referencing_stores)
        defragmenter.defragment()
        expected = properties
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, p in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertTrue(p.equal_payload(val), "Defragmented item:\n[%s]\n"
                            "is not equal to expected:\n[%s]" % (val, p))

    def test_simple_defragment2(self):
        """
        Defragment | 1 | - | 3 | - | 5 |
        Result     | [1] | [3] | [5] |
        """
        p1 = Property(1, True, Property.PropertyType.bool, 9, 0, 0, False)
        p2 = Property(2, True, Property.PropertyType.int, 8, 0, 0, 32)
        p3 = Property(3, True, Property.PropertyType.bool, 7, 0, 0, True)
        p4 = Property(4, True, Property.PropertyType.int, 6, 0, 0, 24)
        p5 = Property(5, True, Property.PropertyType.char, 5, 0, 0, "a")
        properties = [p1, p2, p3, p4, p5]
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
        expected = [p1, p3, p5]
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, p in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertTrue(p.equal_payload(val), "Defragmented item:\n[%s]\n"
                            "is not equal to expected:\n[%s]" % (val, p))

    def test_simple_defragment3(self):
        """
        Defragment | - | 2 | - | 4 | - | 6 |
        Result     | [2] | [4] | [6] |
        """
        p1 = Property(1, True, Property.PropertyType.bool, 9, 0, 0, False)
        p2 = Property(2, True, Property.PropertyType.int, 8, 0, 0, 32)
        p3 = Property(3, True, Property.PropertyType.bool, 7, 0, 0, True)
        p4 = Property(4, True, Property.PropertyType.int, 6, 0, 0, 24)
        p5 = Property(5, True, Property.PropertyType.char, 5, 0, 0, "a")
        p6 = Property(6, True, Property.PropertyType.int, 4, 0, 0, 32)
        properties = [p1, p2, p3, p4, p5, p6]
        base_store = PropertyStore()
        for p in properties:
            base_store.write_item(p)
        delete_idx = [1, 3, 5]
        for i in delete_idx: base_store.delete_item_at_index(i)

        id_store = IdStore(base_store.filename + ".id")
        id_store.get_all_ids = MagicMock(return_value=delete_idx)

        referencing_stores = []

        defragmenter = Defragmenter(base_store, id_store, referencing_stores)
        defragmenter.defragment()
        expected = [p2, p4, p6]
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, p in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertTrue(p.equal_payload(val), "Defragmented item:\n[%s]\n"
                            "is not equal to expected:\n[%s]" % (val, p))

    def test_simple_defragment4(self):
        """
        Defragment | - | - | 3 | 4 | 5 | 6 |
        Result     | [3] | [4] | [5] | [6] |
        """
        p1 = Property(1, True, Property.PropertyType.bool, 9, 0, 0, False)
        p2 = Property(2, True, Property.PropertyType.int, 8, 0, 0, 32)
        p3 = Property(3, True, Property.PropertyType.bool, 7, 0, 0, True)
        p4 = Property(4, True, Property.PropertyType.int, 6, 0, 0, 24)
        p5 = Property(5, True, Property.PropertyType.char, 5, 0, 0, "a")
        p6 = Property(6, True, Property.PropertyType.int, 4, 0, 0, 32)
        properties = [p1, p2, p3, p4, p5, p6]
        base_store = PropertyStore()
        for p in properties:
            base_store.write_item(p)
        delete_idx = [1, 2]
        for i in delete_idx: base_store.delete_item_at_index(i)

        id_store = IdStore(base_store.filename + ".id")
        id_store.get_all_ids = MagicMock(return_value=delete_idx)

        referencing_stores = []

        defragmenter = Defragmenter(base_store, id_store, referencing_stores)
        defragmenter.defragment()
        expected = [p3, p4, p5, p6]
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, p in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertTrue(p.equal_payload(val), "Defragmented item:\n[%s]\n"
                            "is not equal to expected:\n[%s]" % (val, p))

    def test_self_reference_defragment1(self):
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
            self.assertTrue(p.equal_payload(val), "Defragmented item:\n[%s]\n"
                            "is not equal to expected:\n[%s]" % (val, p))

    def test_self_reference_defragment2(self):
        """
        Case with forward references for prev backward references for next
        Defragment | 0->1->3 | - | 1->3->0 | - | 6->5->1 | 0->6->3 |
        Result     | 0->[1]->2 | 1->[3]->0 | 4->[5]->1 | 0->[6]->2 |
        """
        p1 = Property(1, True, Property.PropertyType.bool, 9, 0, 3, False)
        p2 = Property(2, True, Property.PropertyType.int, 8, 1, 3, 32)
        p3 = Property(3, True, Property.PropertyType.bool, 7, 1, 0, True)
        p4 = Property(4, True, Property.PropertyType.int, 6, 3, 5, 24)
        p5 = Property(5, True, Property.PropertyType.char, 5, 6, 1, "a")
        p6 = Property(6, True, Property.PropertyType.int, 4, 0, 3, 32)
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
        p3e = Property(2, True, Property.PropertyType.bool, 7, 1, 0, True)
        p5e = Property(3, True, Property.PropertyType.char, 5, 4, 1, "a")
        p6e = Property(4, True, Property.PropertyType.int, 4, 0, 2, 32)
        expected = [p1e, p3e, p5e, p6e]
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, p in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertTrue(p.equal_payload(val), "Defragmented item:\n[%s]\n"
                            "is not equal to expected:\n[%s]" % (val, p))

    def test_self_reference_defragment3(self):
        """
        Case with no full, continuous blocks so all reference updating is
        done when items are loaded into RAM.
        Defragment | -| - | 0->3->0 | 3->4->5 | 3->5->6 | 5->6->0 |
        Result     | 0->[3]->0 | 1->[4]->3 | 1->[5]->4 | 3->[6]->0 |
        """
        p1 = Property(1, True, Property.PropertyType.bool, 9, 0, 3, False)
        p2 = Property(2, True, Property.PropertyType.int, 8, 1, 3, 32)
        p3 = Property(3, True, Property.PropertyType.bool, 7, 0, 0, True)
        p4 = Property(4, True, Property.PropertyType.int, 6, 3, 5, 24)
        p5 = Property(5, True, Property.PropertyType.char, 5, 3, 6, "a")
        p6 = Property(6, True, Property.PropertyType.int, 4, 5, 0, 32)
        properties = [p1, p2, p3, p4, p5, p6]
        base_store = PropertyStore()
        for p in properties:
            base_store.write_item(p)
        delete_idx = [1, 2]
        for i in delete_idx: base_store.delete_item_at_index(i)

        id_store = IdStore(base_store.filename + ".id")
        id_store.get_all_ids = MagicMock(return_value=delete_idx)

        referencing_stores = []
        defragmenter = Defragmenter(base_store, id_store, referencing_stores)
        defragmenter.defragment()
        # Expected values with self references updated
        p3e = Property(1, True, Property.PropertyType.bool, 7, 0, 0, True)
        p4e = Property(2, True, Property.PropertyType.int, 6, 1, 3, 24)
        p5e = Property(3, True, Property.PropertyType.char, 5, 1, 4, "a")
        p6e = Property(4, True, Property.PropertyType.int, 4, 3, 0, 32)
        expected = [p3e, p4e, p5e, p6e]
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, p in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertTrue(p.equal_payload(val), "Defragmented item:\n[%s]\n"
                            "is not equal to expected:\n[%s]" % (val, p))
