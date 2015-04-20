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
        item_read = store_manager.get_item_at_index(item.index)
        self.assertEquals(item_read, None)
