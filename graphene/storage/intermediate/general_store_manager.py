from graphene.storage.base.id_store import *


class GeneralStoreManager:
    """
    Handles the creation/deletion of nodes to the NodeStore with ID recycling
    """

    def __init__(self, store):
        """
        Creates an instance of the GeneralStoreManager

        :param store: Store instance to manage
        :return: General store manager to handle index recycling
        :rtype: GeneralStoreManager
        """
        self.store = store
        self.idStore = IdStore(store.filename + ".id")

    def create_item(self, index=0, **kwargs):
        """
        Creates an item with the type of the store being managed.
        NOTE: Does not write the created item to the file to allow processing.

        :param index: Index where the item will be created
        :type index: int
        :param kwargs: Arguments to pass to the created item
        :type kwargs: dict
        :return: New item with type STORE_TYPE
        """
        # If no index is given, check for an available ID from the IdStore
        if index == 0:
            index = self.get_indexes()[0]
        # Create a type based on the type our store stores
        return self.store.STORAGE_TYPE(index, **kwargs)

    def write_item(self, item):
        """
        Writes the item to its store file

        :param item: Item to write to file
        :return: Nothing
        :rtype: None
        """
        self.store.write_item(item)

    def delete_item(self, item):
        """
        Deletes the given item from the store and adds the index to its IdStore
        to be recycled

        :return: Nothing
        :rtype: None
        """
        # Get index of item to be deleted
        deleted_index = item.index
        self.delete_item_at_index(deleted_index)

    def delete_item_at_index(self, index):
        """
        Deletes the item at the given index from the store and adds
        the index to its IdStore to be recycled

        :return: Nothing
        :rtype: None
        """
        # Delete the item from the store
        self.store.delete_item_at_index(index)
        # Check if the ID is the last ID in the file, if so then don't add it
        # to the ID store since the file will be truncated instead of zeroed
        if index != self.store.get_last_file_index() - 1:
            # Add the index to the IdStore, so it can be recycled
            self.idStore.store_id(index)

    def get_item_at_index(self, index):
        """
        Gets the item from the store at the given index

        :param index: Index to get the item from
        :type index: int
        :return: Item at that index
        """
        return self.store.item_at_index(index)

    def get_indexes(self, amount=1):
        """
        Get the requested number of indexes

        :param amount: Amount of indexes to retrieve
        :type amount: int
        :return: List of indexes
        :rtype: list
        """
        # List of IDs
        ids = []
        # Create list of IDs
        for i in range(0, amount):
            # Get ID from ID store
            cur_index = self.idStore.get_id()
            # No more IDs, return list with last indexes of the store file
            if cur_index == IdStore.NO_ID:
                last_index = self.store.get_last_file_index()
                ids += [last_index + j for j in range(0, amount - i)]
                # Done getting IDs, got them from the end of the file
                break
            # Append the index from the ID store
            else:
                ids.append(cur_index)
        # Return list of ids
        return ids
