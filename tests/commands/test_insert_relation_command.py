import unittest

from graphene.commands import InsertRelationCommand
from graphene.storage import (StorageManager, GrapheneStore, Property, Relationship, Node)
from graphene.server.server import GrapheneServer
from graphene.utils.conversion import TypeConversion
from graphene.errors import TypeMismatchException

class TestInsertRelationCommand(unittest.TestCase):
    def setUp(self):
        GrapheneStore.TESTING = True
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()
        self.server = GrapheneServer()
        self.sm = self.server.storage_manager
        self.node_manager = self.sm.node_manager

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        del self.sm
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_bad_rel_prop(self):
        t = self.sm.create_node_type("T", (("a", "int"),))
        r = self.sm.create_relationship_type("R", (("a", "string"),))
        n1, p1 = self.sm.insert_node(t, ((Property.PropertyType.int, 1),))
        n2, p2 = self.sm.insert_node(t, ((Property.PropertyType.int, 3),))
        cmd = self.server.parseString("INSERT RELATION T(a=1)-[R(1)]->T(a=3)")[0]

        # Trying to insert an int for a string should raise an error
        with self.assertRaises(TypeMismatchException):
            cmd.execute(self.sm)

    def test_no_self_rels(self):
        t = self.sm.create_node_type("T", (("a", "int"),))
        r = self.sm.create_relationship_type("R", (("a", "int"),))
        n1, p1 = self.sm.insert_node(t, ((Property.PropertyType.int, 1),))
        cmd = self.server.parseString("INSERT RELATION T(a=1)-[R(1)]->T(a=1)")[0]

        rels = cmd.execute(self.sm)
        # Nodes can't be connected to themselves, so no relations should have
        # been made
        self.assertEquals(len(rels), 0)

    def test_insert_single_relation(self):
        t = self.sm.create_node_type("T", (("a", "int"),))
        r = self.sm.create_relationship_type("R", (("a", "int"),))
        n1, p1 = self.sm.insert_node(t, ((Property.PropertyType.int, 1),))
        n2, p2 = self.sm.insert_node(t, ((Property.PropertyType.int, 3),))

        cmd = self.server.parseString("INSERT RELATION T(a=1)-[R(1)]->T(a=3)")[0]

        rels = cmd.execute(self.sm)
        self.assertEquals(len(rels), 1) # Should only have one relation

        rel_idx = rels[0].index
        rel, props = self.sm.relprop[rel_idx]

        # Check that relation has correct data
        self.assertEquals(rel.relType, r.index)
        self.assertEquals(rel.direction, Relationship.Direction.right)
        self.assertEquals(rel.firstNodeId, n1.index)
        self.assertEquals(rel.secondNodeId, n2.index)
        self.assertEquals(rel.firstPrevRelId, 0)
        self.assertEquals(rel.firstNextRelId, 0)
        self.assertEquals(rel.propId, props[0].index)

        # Check that nodes were updated with relation
        self.assertEquals(n1.relId, rel_idx)
        self.assertEquals(n2.relId, rel_idx)
