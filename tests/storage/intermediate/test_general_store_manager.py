import unittest

from graphene.storage.intermediate.general_store_manager import *
from graphene.storage.base.node_store import *


class TestGeneralStoreManagerMethods(unittest.TestCase):
    # Test the GeneralStoreManager with the NodeStore, this can be changed
    # to any store and the tests must work the same, assuming NodeStore-specific
    # features are changed
    TEST_STORE = NodeStore

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
        Test that initializing a GeneralStoreManager succeeds (file is opened)
        """
        try:
            GeneralStoreManager(self.TEST_STORE())
        except IOError:
            self.fail("GeneralStoreManager initializer failed: %s"
                      "db file failed to open." % self.TEST_STORE.__name__)

    def test_double_init(self):
        """
        Test that initializing a GeneralStoreManger succeeds when repeated;
        i.e. the old file is reopened and no errors occur.
        """
        try:
            GeneralStoreManager(self.TEST_STORE())
        except IOError:
            self.fail("GeneralStoreManager initializer failed: %s"
                      "db file failed to open." % self.TEST_STORE.__name__)
        try:
            GeneralStoreManager(self.TEST_STORE())
        except IOError:
            self.fail("GeneralStoreManager initializer failed on second"
                      "attempt: %s db file failed to open."
                      % self.TEST_STORE.__name__)

    def test_create_item(self):
        """
        Tests creation of an empty item when no keyword arguments are given
        """
        store_manager = GeneralStoreManager(self.TEST_STORE())

        # Create an item with type TEST_STORE.STORAGE_TYPE (pass no kwargs)
        item = store_manager.create_item()
        # Store the item
        store_manager.write_item(item)
        # Check that the created item is as expected
        self.assertEquals(item, self.TEST_STORE.STORAGE_TYPE(index=item.index))
        # Check that when reading the item from the store it is the same
        self.assertEquals(item, store_manager.get_item_at_index(item.index))

    def test_delete_item(self):
        """
        Test the creation and deletion of an item when no keywords arguments
        are given
        """
        store_manager = GeneralStoreManager(self.TEST_STORE())

        # Create an item with type TEST_STORE.STORAGE_TYPE (pass no kwargs)
        item = store_manager.create_item()
        # Store the item
        store_manager.write_item(item)
        # Check that the created item is as expected
        self.assertEquals(item, self.TEST_STORE.STORAGE_TYPE(index=item.index))
        # Check that when reading the item from the store it is the same
        self.assertEquals(item, store_manager.get_item_at_index(item.index))

        # Delete the item
        store_manager.delete_item(item)

        # Read the item index to make sure the item is deleted
        # Since the item is at the end of the file, the file will be truncated
        # so this should return EOF
        item_read = store_manager.get_item_at_index(item.index)
        self.assertEquals(item_read, EOF)

    def test_get_indexes(self):
        """
        Test that get indexes returns the expected number of recycled IDs or
        last file indexes.
        """
        # import pytest
        # pytest.set_trace()
        store_manager = GeneralStoreManager(self.TEST_STORE())
        # Get indexes (should be the last file indexes)
        index_list = store_manager.get_indexes(2)
        # Check that the indexes are as expected (last file indexes)
        index1 = index_list[0]
        index2 = index_list[1]
        self.assertEquals(index1, store_manager.store.get_last_file_index())
        self.assertEquals(index2, store_manager.store.get_last_file_index() + 1)
        # Create and write two items with the given index
        item1 = store_manager.create_item(index1)
        item2 = store_manager.create_item(index2)
        store_manager.write_item(item1)
        store_manager.write_item(item2)
        # Delete the item, the index should now be in the recycled IDs
        store_manager.delete_item_at_index(index1)

        # Get two indexes, now one should be a recycled index i.e. 1, and the
        # other should be the last file index
        index_list = store_manager.get_indexes(2)
        index1_new = index_list[0]
        index2 = index_list[1]
        # Check that the first index is the recycled one
        self.assertEquals(index1, index1_new)
        # And that the last index is the last file index
        self.assertEquals(store_manager.store.get_last_file_index(), index2)

        # Create two items with the indexes
        item1 = store_manager.create_item(index1)
        item2 = store_manager.create_item(index2)
        # And a third without an index argument
        item3 = store_manager.create_item()
        # Write the items
        store_manager.write_item(item1)
        store_manager.write_item(item2)
        store_manager.write_item(item3)
        # Delete the second item (second index)
        store_manager.delete_item_at_index(index2)

        # Now when we get 4 IDs, one should be the recycled second index, and
        # the other 3 should be the last file index with 2 increments
        index_list = store_manager.get_indexes(4)
        last_index = store_manager.store.get_last_file_index()
        self.assertEquals(index_list[0], index2)
        self.assertEquals(index_list[1], last_index)
        self.assertEquals(index_list[2], last_index + 1)
        self.assertEquals(index_list[3], last_index + 2)
