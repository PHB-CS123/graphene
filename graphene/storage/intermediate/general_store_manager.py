from graphene.storage.id_store import *


class GeneralStoreManager:
    """
    Handles the creation/deletion of nodes to the NodeStore with ID recycling
    """

    def __init__(self, store):
        """
        Creates an instance of the GeneralStoreManager

        :param store: Store to manage
        :return: General store manager to handle index recycling
        :rtype: GeneralStoreManager
        """
        self.store = store
        self.idStore = IdStore(store.FILE_NAME + ".id")

    def create_item(self):
        """
        Creates an item with the type of the store being managed

        :return: New item with type STORE_TYPE
        """
        # Check for an available ID from the IdStore
        available_id = self.idStore.get_id()
        # If no ID is available, get the last index of the file
        if available_id == IdStore.NO_ID:
            available_id = self.store.get_last_file_index()
        # Create a type based on the type our store stores
        return self.store.STORAGE_TYPE(available_id)

    def delete_item(self, item):
        """
        Deletes the given item from the store and adds the index to its IdStore
        to be recycled

        :return: Nothing
        :rtype: None
        """
        # Get index of item to be deleted
        deleted_index = item.index
        # Delete the item from the store
        self.store.delete_item(item)
        # Add the index to the IdStore, so it can be recycled
        self.idStore.store_id(deleted_index)

    def get_item_at_index(self, index):
        """
        Gets the item from the store at the given index

        :param index: Index to get the item from
        :type index: int
        :return: Item at that index
        """