import unittest

from tests_e2e.defrag.e2e_test_defragmenter_base import E2ETestDefragmenterBase
from graphene.storage.base.graphene_store import GrapheneStore
from graphene.utils.pretty_printer import PrettyPrinter


class TestDefragmenterSimple(unittest.TestCase):

    SCRIPTS_DIR = "tests_e2e/defrag/Scripts/"
    SETUP_CMDS_FILENAME = "node-matching-4500-people-fixture.gp"
    DELETE_CMDS_FILENAME = "node-matching-4500-people-deletion.gp"
    QUERY_CMDS_FILENAME = "node-matching-4500-people.gp"

    def setUp(self):
        """
        Set up the GrapheneStore so that it writes datafiles to the testing
        directory
        """
        GrapheneStore.TESTING = True
        PrettyPrinter.NO_COLORS = True

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_defrag_control(self):
        if self.get_test_base().execute_with_no_defrag():
            self.fail("Running control test failed.")

    def test_defrag(self):
        if self.get_test_base().execute_with_defrag():
            self.fail("Running defragmentation tests failed.")

    @classmethod
    def get_test_base(cls):
        setup_cmds_filename = cls.SCRIPTS_DIR + cls.SETUP_CMDS_FILENAME
        delete_cmds_filename = cls.SCRIPTS_DIR + cls.DELETE_CMDS_FILENAME
        query_cmds_filename = cls.SCRIPTS_DIR + cls.QUERY_CMDS_FILENAME
        return E2ETestDefragmenterBase(setup_cmds_filename,
                                       query_cmds_filename,
                                       delete_cmds_filename)