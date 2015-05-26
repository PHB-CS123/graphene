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

    def __del__(self):
        del self.idStore
        del self.store

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
        # Get last file index before deletion
        last_file_index = self.store.get_last_file_index()
        # Delete the item from the store
        self.store.delete_item_at_index(index)
        # Check if the ID is the last ID in the file, if so then don't add it
        # to the ID store since the file will be truncated instead of zeroed
        if index != last_file_index - 1:
            # Add the index to the IdStore, so it can be recycled
            self.idStore.store_id(index)
        # # In this case, truncation will be needed
        else:
            self.truncate_store()

    def truncate_store(self):
        """
        Truncate the last zeroed items of the store

        :return: Nothing
        :rtype: None
        """
        # Get free IDs
        ids = self.idStore.get_all_ids()
        # No IDs to truncate, done
        if not ids:
            return
        # Get all file IDs and sort them in reverse order
        ids.sort(reverse=True)
        # Write them back in this reverse order to prevent future
        # fragmentation (lower IDs will be popped from the end)
        self.idStore.write_all_ids(ids)

        # Now find out how many IDs need truncation
        last_file_index = self.store.get_last_file_index()
        trunc_amt = self.truncate_amount(ids, last_file_index)
        # Finally truncate this many items
        self.store.truncate_file(trunc_amt)

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

    @staticmethod
    def truncate_amount(ids, last_file_index):
        """
        Number IDS that need truncation from the given list of free IDs

        :param ids: List of free IDs, MUST BE SORTED IN DESCENDING ORDER
        :type ids: list
        :param last_file_index: Index where the next item would be created
        :type last_file_index: int
        :return: Number of IDs to truncate
        :rtype: int
        """
        # Empty list, return
        if not ids:
            return None
        # Count the number of consecutive IDs starting at last_file_index - 1
        # Complexity: O(n)
        trunc_amt = 0
        cur = last_file_index - 1
        for i in ids:
            if i == cur:
                trunc_amt += 1
                cur -= 1
            else:
                break
        return trunc_amt

    @staticmethod
    def defrag_ids(ids, last_file_index):
        """
        IDs that need defragmentation from the given list of free IDs

        :param ids: List of free IDs
        :type ids: list
        :param last_file_index: Index where next item would be created
        :type last_file_index: int
        :return: List of IDs needing defragmentation
        :rtype: list
        """
        # Empty list, return
        if not ids:
            return None
        # Get the smallest element
        smallest = min(ids)
        # Items that can be fragmented start at the smallest non-free ID
        pos_frag = set(range(smallest, last_file_index))
        # The set difference between a range starting at the smallest
        # element, ending at the last file index and the free ids will
        # be the fragmented IDs
        return list(pos_frag - set(ids))
