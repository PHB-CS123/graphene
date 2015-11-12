import unittest
from mock import MagicMock

from graphene.storage.base.graphene_store import GrapheneStore
from graphene.storage.base.id_store import IdStore
from graphene.storage.base.property_store import PropertyStore, Property
from graphene.storage.defrag.defragmenter import *


class TestDefragmenterMethods(unittest.TestCase):
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
        p1 = Property(1, True, Property.PropertyType.bool, 9, 0, 2, False)
        p2 = Property(2, True, Property.PropertyType.int, 8, 1, 3, 32)
        p3 = Property(3, True, Property.PropertyType.bool, 7, 2, 4, True)
        p4 = Property(4, True, Property.PropertyType.int, 6, 3, 5, 24)
        p5 = Property(5, True, Property.PropertyType.char, 5, 4, 6, "a")
        p6 = Property(6, True, Property.PropertyType.int, 4, 5, 0, 32)
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
            self.assertTrue(p.equal_payload(val),
                            "Defragmented item: %s is not equal to expected: %s"
                            % (val, p))

    def test_simple_defragment2(self):
        """
        Defragment | 1 | - | 3 | - | 5 |
        Result     | 1 | 3 | 5 |
        """
        p1 = Property(1, True, Property.PropertyType.bool, 9, 0, 2, False)
        p2 = Property(2, True, Property.PropertyType.int, 8, 1, 3, 32)
        p3 = Property(3, True, Property.PropertyType.bool, 7, 2, 4, True)
        p4 = Property(4, True, Property.PropertyType.int, 6, 3, 5, 24)
        p5 = Property(5, True, Property.PropertyType.char, 5, 4, 6, "a")
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
            self.assertTrue(p.equal_payload(val),
                            "Defragmented item: %s is not equal to expected: %s"
                            % (val, p))

    def test_simple_defragment3(self):
        """
        Defragment | - | 2 | - | 4 | - | 6 |
        Result     | 2 | 4 | 6 |
        """
        p1 = Property(1, True, Property.PropertyType.bool, 9, 0, 2, False)
        p2 = Property(2, True, Property.PropertyType.int, 8, 1, 3, 32)
        p3 = Property(3, True, Property.PropertyType.bool, 7, 2, 4, True)
        p4 = Property(4, True, Property.PropertyType.int, 6, 3, 5, 24)
        p5 = Property(5, True, Property.PropertyType.char, 5, 4, 6, "a")
        p6 = Property(6, True, Property.PropertyType.int, 4, 5, 0, 32)
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
            self.assertTrue(p.equal_payload(val),
                            "Defragmented item: %s is not equal to expected: %s"
                            % (val, p))

    def test_simple_defragment4(self):
        """
        Defragment | - | - | 3 | 4 | 5 | 6 |
        Result     | 3 | 4 | 5 | 6 |
        """
        p1 = Property(1, True, Property.PropertyType.bool, 9, 0, 2, False)
        p2 = Property(2, True, Property.PropertyType.int, 8, 1, 3, 32)
        p3 = Property(3, True, Property.PropertyType.bool, 7, 2, 4, True)
        p4 = Property(4, True, Property.PropertyType.int, 6, 3, 5, 24)
        p5 = Property(5, True, Property.PropertyType.char, 5, 4, 6, "a")
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
        expected = [p3, p4, p5, p6]
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, p in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertTrue(p.equal_payload(val),
                            "Defragmented item: %s is not equal to expected: %s"
                            % (val, p))
