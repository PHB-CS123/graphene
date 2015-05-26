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

    def test_delete_item_truncate(self):
        """
        Test that the file is properly truncated when a delete occurs
        """
        store_manager = GeneralStoreManager(self.TEST_STORE())

        # Create and write one blank item
        store_manager.create_item()
        # Store the file size with only one item
        one_item_size = store_manager.store.get_file_size()
        # Create and write 3 more items
        item2 = store_manager.create_item()
        item3 = store_manager.create_item()
        item4 = store_manager.create_item()

        # Delete the 2nd, then 3rd, then 4th item, this should leave items
        # 2 and 3 untruncated. If the file is properly truncated, it should
        # have the same size as with only item 1
        store_manager.delete_item(item2)
        store_manager.delete_item(item3)
        store_manager.delete_item(item4)
        self.assertEquals(one_item_size, store_manager.store.get_file_size())

    def test_get_indexes(self):
        """
        Test that get indexes returns the expected number of recycled IDs or
        last file indexes.
        """
        store_manager = GeneralStoreManager(self.TEST_STORE())
        # Get indexes (should be the last file indexes)
        index_list = store_manager.get_indexes(2)
        # Check that the indexes are as expected (last file indexes)
        index1 = index_list[0]
        index2 = index_list[1]
        self.assertEquals(index1, store_manager.store.get_last_file_index())
        self.assertEquals(index2, store_manager.store.get_last_file_index() + 1)
        # Create and write two items with the given index
        store_manager.create_item(index1)
        store_manager.create_item(index2)
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

        # Create and write two items with the indexes
        store_manager.create_item(index1_new)
        store_manager.create_item(index2)
        # And a third without an index argument
        store_manager.create_item()
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

    def test_truncate_amount(self):
        """
        Test that the method returns the correct number of IDs to truncate
        """
        # Check that when passing an empty array, the method returns None
        self.assertIsNone(GeneralStoreManager.truncate_amount([], 10))
        # Free IDs
        ids = [1, 2, 4, 8, 9]
        ids.sort(reverse=True)
        # Index where a new item would be placed
        last_file_index = 10
        # Correct number of items to truncate
        correct_trunc_amt = 2
        # Make sure the results are as expected
        result = GeneralStoreManager.truncate_amount(ids, last_file_index)
        self.assertEquals(result, correct_trunc_amt)

    def test_defrag_ids(self):
        """
        Test that the method returns the correct IDs that need defragmentation
        """
        # Check that when passing an empty array, the method returns None
        self.assertIsNone(GeneralStoreManager.defrag_ids([], 10))
        # Free IDs
        ids = [4, 3, 2, 6]
        # Index where a new item would be placed
        last_index = 10
        # Items that need defragmentation
        defrag = [5, 7, 8, 9]
        # Make sure results are as expected
        results = sorted(GeneralStoreManager.defrag_ids(ids, last_index))
        self.assertEquals(results, defrag)
