import unittest
from mock import MagicMock

from graphene.storage.base.graphene_store import GrapheneStore
from graphene.storage.base.id_store import IdStore
from graphene.storage.base.property_store import PropertyStore, Property
from graphene.storage.base.node_store import NodeStore, Node
from graphene.storage.base.relationship_store import RelationshipStore, Relationship
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

    def test_complex_defragment_1(self):
        """
        Defragment a property store that is referenced by a node store.
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
        map(lambda p: base_store.write_item(p), properties)
        delete_idx = [2, 4]
        map(lambda i: base_store.delete_item_at_index(i), delete_idx)

        id_store = IdStore(base_store.filename + ".id")
        id_store.get_all_ids = MagicMock(return_value=delete_idx)

        # Create node referencing store
        n1 = Node(1, True, 0, 5, 0)
        n2 = Node(2, True, 0, 3, 0)
        n3 = Node(3, True, 0, 1, 0)
        n4 = Node(4, True, 0, 4, 0)
        n5 = Node(5, True, 0, 0, 0)
        nodes = [n1, n2, n3, n4, n5]
        node_store = NodeStore()
        map(lambda n: node_store.write_item(n), nodes)

        referencing_stores = [node_store]

        defragmenter = Defragmenter(base_store, id_store, referencing_stores)
        defragmenter.defragment()

        # Check that the base store is defragmented correctly
        expected = [p1, p3, p5]
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, p in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertTrue(p.equal_payload(val), "Defragmented item:\n[%s]\n"
                            "is not equal to expected:\n[%s]" % (val, p))

        # Create expected updated node references
        n1e = Node(1, True, 0, 3, 0)
        n2e = Node(2, True, 0, 2, 0)
        n3e = Node(3, True, 0, 1, 0)
        n4e = Node(4, True, 0, 4, 0)
        n5e = Node(5, True, 0, 0, 0)
        expected = [n1e, n2e, n3e, n4e, n5e]
        # Check that the referencing store is defragmented correctly
        self.assertEqual(node_store.count(), len(expected),
                         "Ref. store block count does not equal expected count")
        for i, n in enumerate(expected, 1):
            val = node_store.item_at_index(i)
            self.assertEqual(val, n, "Defragmented reference:\n[%s]\n"
                             "is not equal to expected:\n[%s]" % (val, n))

    def test_complex_defragment_2(self):
        """
        Defragment a property store that is referenced by a node store and a
        relationship store.
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
        map(lambda p: base_store.write_item(p), properties)
        delete_idx = [2, 4]
        map(lambda i: base_store.delete_item_at_index(i), delete_idx)

        id_store = IdStore(base_store.filename + ".id")
        id_store.get_all_ids = MagicMock(return_value=delete_idx)

        # Create node referencing store
        n1 = Node(1, True, 0, 5, 0)
        n2 = Node(2, True, 0, 3, 0)
        n3 = Node(3, True, 0, 1, 0)
        n4 = Node(4, True, 0, 4, 0)
        n5 = Node(5, True, 0, 0, 0)
        nodes = [n1, n2, n3, n4, n5]
        node_store = NodeStore()
        map(lambda n: node_store.write_item(n), nodes)

        # Create relationship referencing store
        r1 = Relationship(1, True, Relationship.Direction.left, 1, 3, 5, 1, 1, 3, 3, 1)
        r2 = Relationship(2, True, Relationship.Direction.left, 3, 5, 1, 3, 5, 5, 1, 3)
        r3 = Relationship(3, True, Relationship.Direction.left, 5, 1, 3, 5, 3, 1, 6, 5)
        rels = [r1, r2, r3]
        rel_store = RelationshipStore()
        map(lambda r: rel_store.write_item(r), rels)

        referencing_stores = [node_store, rel_store]

        defragmenter = Defragmenter(base_store, id_store, referencing_stores)
        defragmenter.defragment()

        # Check that the base store is defragmented correctly
        expected = [p1, p3, p5]
        self.assertEqual(base_store.count(), len(expected),
                         "Base store block count does not equal expected count")
        for i, p in enumerate(expected, 1):
            val = base_store.item_at_index(i)
            self.assertTrue(p.equal_payload(val), "Defragmented item:\n[%s]\n"
                            "is not equal to expected:\n[%s]" % (val, p))

        # Create expected updated node references
        n1e = Node(1, True, 0, 3, 0)
        n2e = Node(2, True, 0, 2, 0)
        n3e = Node(3, True, 0, 1, 0)
        n4e = Node(4, True, 0, 4, 0)
        n5e = Node(5, True, 0, 0, 0)
        expected = [n1e, n2e, n3e, n4e, n5e]
        # Check that the referencing store is defragmented correctly
        self.assertEqual(node_store.count(), len(expected),
                         "Ref. store block count does not equal expected count")
        for i, n in enumerate(expected, 1):
            val = node_store.item_at_index(i)
            self.assertEqual(val, n, "Defragmented reference:\n[%s]\n"
                             "is not equal to expected:\n[%s]" % (val, n))

        # Create expected updated relationship references
        r1e = Relationship(1, True, Relationship.Direction.left, 1, 3, 5, 1, 1, 3, 3, 1)
        r2e = Relationship(2, True, Relationship.Direction.left, 3, 5, 1, 3, 5, 5, 1, 2)
        r3e = Relationship(3, True, Relationship.Direction.left, 5, 1, 3, 5, 3, 1, 6, 3)
        expected = [r1e, r2e, r3e]
        # Check that the referencing store is defragmented correctly
        self.assertEqual(rel_store.count(), len(expected),
                         "Ref. store block count does not equal expected count")
        for i, r in enumerate(expected, 1):
            val = rel_store.item_at_index(i)
            self.assertEqual(val, r, "Defragmented reference:\n[%s]\n"
                             "is not equal to expected:\n[%s]" % (val, r))

    def test_self_reference_complex_defragment(self):
        """
        Simple link of forward references for next and backward refs for prev.
        Test defragmentation of these references along with the referencing
        store.
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
        map(lambda p: base_store.write_item(p), properties)
        delete_idx = [2, 4]
        map(lambda i: base_store.delete_item_at_index(i), delete_idx)

        id_store = IdStore(base_store.filename + ".id")
        id_store.get_all_ids = MagicMock(return_value=delete_idx)

        # Create node referencing store
        n1 = Node(1, True, 0, 5, 0)
        n2 = Node(2, True, 0, 3, 0)
        n3 = Node(3, True, 0, 1, 0)
        n4 = Node(4, True, 0, 4, 0)
        n5 = Node(5, True, 0, 0, 0)
        nodes = [n1, n2, n3, n4, n5]
        node_store = NodeStore()
        map(lambda n: node_store.write_item(n), nodes)

        referencing_stores = [node_store]

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

        # Create expected updated node references
        n1e = Node(1, True, 0, 3, 0)
        n2e = Node(2, True, 0, 2, 0)
        n3e = Node(3, True, 0, 1, 0)
        n4e = Node(4, True, 0, 4, 0)
        n5e = Node(5, True, 0, 0, 0)
        expected = [n1e, n2e, n3e, n4e, n5e]
        # Check that the referencing store is defragmented correctly
        self.assertEqual(node_store.count(), len(expected),
                         "Ref. store block count does not equal expected count")
        for i, n in enumerate(expected, 1):
            val = node_store.item_at_index(i)
            self.assertEqual(val, n, "Defragmented reference:\n[%s]\n"
                             "is not equal to expected:\n[%s]" % (val, n))