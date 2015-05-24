import unittest

from graphene.storage.base.id_store import *


class TestIdStoreMethods(unittest.TestCase):
    TEST_FILENAME = "graphenestore.teststore.db.id"

    def setUp(self):
        GrapheneStore.TESTING = True

    def tearDown(self):
        """
        Clean the database so that the tests are independent of one another
        """
        graphene_store = GrapheneStore()
        graphene_store.remove_test_datafiles()

    def test_init(self):
        """
        Test that initializing an IdStore succeeds (file is opened)
        """
        try:
            IdStore(self.TEST_FILENAME)
        except IOError:
            self.fail("IdStore initializer failed: id file failed to open.")

    def test_double_init(self):
        """
        Test that initializing an IdStore succeeds when repeated;
        i.e. the old file is reopened and no errors occur.
        """
        try:
            IdStore(self.TEST_FILENAME)
        except IOError:
            self.fail("IdStore initializer failed: id file failed to open.")
        try:
            IdStore(self.TEST_FILENAME)
        except IOError:
            self.fail("IdStore initializer failed on second attempt: "
                      "id file failed to open.")

    def read_id_empty_file(self):
        """
        Test that reading an ID from a file with no ids returns NO_ID
        """
        id_store = IdStore(self.TEST_FILENAME)
        # Read ID from empty IdStore file
        no_id = id_store.get_id()
        # Check that the NO_ID value was returned
        self.assertEquals(no_id, IdStore.NO_ID)

    def test_write_read_id(self):
        """
        Test that when an ID is written, it can be read.
        """
        id_store = IdStore(self.TEST_FILENAME)

        # Write ID to file
        id_written = 42
        id_store.store_id(id_written)

        # Read ID from file
        id_read = id_store.get_id()
        # Expect to get no ID
        no_id = id_store.get_id()

        # Check that the IDs are the same
        self.assertEquals(id_written, id_read)
        # Check that the NO_ID value was returned
        self.assertEquals(no_id, IdStore.NO_ID)

    def test_write_read_ids(self):
        """
        Test that when 2 IDs are written, they are read back in the
        expected order.
        """
        id_store = IdStore(self.TEST_FILENAME)

        # Write 2 IDs to file
        id_written_1 = 42
        id_written_2 = 21
        id_store.store_id(id_written_1)
        id_store.store_id(id_written_2)

        # Read IDs from the file in reverse order
        id_read_2 = id_store.get_id()
        id_read_1 = id_store.get_id()
        # Expect to get no ID
        no_id = id_store.get_id()

        # Check that the IDs are the same
        self.assertEquals(id_written_1, id_read_1)
        self.assertEquals(id_written_2, id_read_2)
        # Check that the NO_ID value was returned
        self.assertEquals(no_id, IdStore.NO_ID)

    def test_write_read_write_ids(self):
        """
        Test that when an ID is written, read, and another is written, they
        are read as expected.
        """
        id_store = IdStore(self.TEST_FILENAME)

        # Write one ID to the file
        id_written_1 = 42
        id_store.store_id(id_written_1)
        # Read it back
        id_read_1 = id_store.get_id()
        # Check that the IDs are the same
        self.assertEquals(id_written_1, id_read_1)

        # Write another
        id_written_2 = 21
        id_store.store_id(id_written_2)
        # Read it back
        id_read_2 = id_store.get_id()
        # Check that the IDs are the same
        self.assertEquals(id_written_2, id_read_2)

        # Expect to get no ID
        no_id = id_store.get_id()
        # Check that the NO_ID value was returned
        self.assertEquals(no_id, IdStore.NO_ID)

    def test_get_all_ids_none(self):
        """
        Test that when no IDs are available, the method returns None
        """
        id_store = IdStore(self.TEST_FILENAME)
        self.assertIsNone(id_store.get_all_ids())

    def test_get_all_ids(self):
        """
        Test that all IDs are returned from the ID store
        """
        id_store = IdStore(self.TEST_FILENAME)

        # Write 3 IDs to the file
        id_written_1 = 42
        id_written_2 = 10
        id_written_3 = 12
        id_store.store_id(id_written_1)
        id_store.store_id(id_written_2)
        id_store.store_id(id_written_3)

        # Make sure the 3 IDs are read
        ids = [id_written_1, id_written_2, id_written_3]
        self.assertEquals(id_store.get_all_ids(), ids)

    def test_write_all_ids(self):
        """
        Test that overwriting an ID store works
        """
        id_store = IdStore(self.TEST_FILENAME)

        # Write 3 IDs to the file
        id_written_1 = 42
        id_written_2 = 10
        id_written_3 = 12
        id_store.store_id(id_written_1)
        id_store.store_id(id_written_2)
        id_store.store_id(id_written_3)

        # Make sure they are in the file as expected
        ids = [id_written_1, id_written_2, id_written_3]
        self.assertEquals(id_store.get_all_ids(), ids)

        # Overwrite the file with new IDs
        overwrite = [1, 2, 3]
        try:
            id_store.write_all_ids(overwrite)
        except IOError:
            self.fail("IdStore overwrite failed: id file failed to open.")
        # Make sure the new IDs have been overwritten
        self.assertEquals(id_store.get_all_ids(), overwrite)
