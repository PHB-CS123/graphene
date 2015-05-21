from graphene.storage.intermediate.general_name_manager import *
from graphene.storage.base.array_store import *

from itertools import chain


class GeneralArrayManager:
    """
    Handles reading/writing every type of array
    """

    STR_ARRAY_FILENAME = "graphenestore.arraystore.strings.db"

    def __init__(self, block_size=40, string_block_size=10):
        # Size of array blocks. Must be a multiple of 8
        self.blockSize = block_size
        # Create a manager for the array store
        self.storeManager = GeneralStoreManager(ArrayStore(block_size))
        # Create a manager for the strings in string arrays
        self.stringStoreManager = GeneralNameManager(self.STR_ARRAY_FILENAME,
                                                     string_block_size)

    def write_array(self, array, array_type):
        """
        Write the variable-length array to the array store

        :param array: Array to write
        :type array: list
        :param array_type: type of array
        :type array_type: PropertyType
        :return: Starting index of the stored array
        :rtype: int
        """
        # TODO: subclass the linked list creation with the general_name_manager

        # Create an array with string IDs for all the string items
        if array_type == Property.PropertyType.stringArray:
            array = self.string_ids_for_strings(array)

        # Get parts of the array (separated based on the block size and type)
        capacity = ArrayStore.capacity_for_type(array_type, self.blockSize)
        parts = self.array_chunks(array, capacity)

        # Number of parts we need to store
        amt_parts = len(parts)
        # Get IDs to store the blocks into
        ids = self.storeManager.get_indexes(amt_parts)

        # Block of length 1
        if amt_parts == 1:
            kwargs = {'in_use': False,
                      'array_type': array_type,
                      'previous_block': 0,
                      'amount': len(parts[0]),
                      'next_block': 0,
                      'items': parts[0]}
        else:
            kwargs = {'in_use': False,
                      'array_type': array_type,
                      'previous_block': 0,
                      'amount': len(parts[0]),
                      'next_block': ids[1],
                      'items': parts[0]}
        # Create first block using kwargs
        block = self.storeManager.create_item(ids[0], **kwargs)
        # Write it to the file
        self.storeManager.write_item(block)
        # First index in linked list
        first_index = ids[0]

        # Create rest of linked list
        for i in range(1, amt_parts):
            # Last item in linked list
            if i == amt_parts - 1:
                kwargs = {'in_use': False,
                          'array_type': array_type,
                          'previous_block': ids[i - 1],
                          'amount': len(parts[i]),
                          'next_block': 0,
                          'items': parts[i]}
            # Create kwargs for middle block
            else:
                kwargs = {'in_use': False,
                          'array_type': array_type,
                          'previous_block': ids[i - 1],
                          'amount': len(parts[i]),
                          'next_block': ids[i + 1],
                          'items': parts[i]}
            # Create next block
            block = self.storeManager.create_item(ids[i], **kwargs)
            # Write it to the file
            self.storeManager.write_item(block)
        # Return the first index of the array in the store
        return first_index

    def read_array_at_index(self, index):
        """
        Reads the array at the given index (coalescing array blocks)

        :param index: Starting index of the array
        :type index: int
        :return: Array at the index
        :rtype: list
        """
        # Create an empty list where the array blocks will be stored
        array = []
        # Initialize array type to be undefined
        array_type = Property.PropertyType.undefined
        # The array index will be 0 when there are no more blocks
        while index != 0:
            # Get array block
            array_block = self.storeManager.get_item_at_index(index)
            # Check if either the block was deleted or the linked list was
            # broken (only part of a block was deleted)
            if array_block is None:
                return None
            elif array_block is EOF:
                raise EOFError("Corrupted data, unexpected EOF.")
            # Get the type of the array
            array_type = array_block.type
            # Add the next array block to the list
            array.append(array_block.items)
            # Update the index with the index of the next block
            index = array_block.nextBlock

        # Done, combine the array blocks
        array = self.combine_arrays(array)

        # Get strings for the string IDs if the array is a string array
        if array_type == Property.PropertyType.stringArray:
            return self.strings_for_string_ids(array)
        else:
            return array

    def delete_array_at_index(self, index):
        """
        Deletes the array at the given index

        :param index: Index of array to delete
        :type index: int
        :return: Whether the delete succeeded
        :rtype: bool
        """
        # Store the starting index to check if deletion is
        # starting from beginning of linked list
        start_index = index
        # Iterate until we reach the end of the list
        while index != 0:
            # Get current array block
            array_block = self.storeManager.get_item_at_index(index)
            # Check if either the array was deleted, or the linked list
            # was broken (only part of a block was deleted)
            if array_block is None or array_block is EOF:
                return False
            # Make sure that deletion is starting from start of the linked list
            elif index == start_index and array_block.previousBlock != 0:
                raise IndexError("Cannot begin deletion from non-start index")
            # Get the next index
            next_index = array_block.nextBlock
            # Delete the current block
            self.storeManager.delete_item_at_index(index)
            # Update index to the next index
            index = next_index
        return True

    def find_array_items(self, items, limit=0, array_type=None):
        """
        Finds the starting index of the arrays containing the requested item(s)
        WARNING: not efficient

        :param items: Item(s) to look for
        :type items: list
        :param limit: Matches to limit the search to (can speed up search)
        :type limit: int
        :param array_type: Type of array searching for (can speed up search)
        :type array_type: PropertyType
        :return: List of starting indexes of the arrays containing the items
        :rtype: list
        """
        # Last index in the array store file
        last_index = self.storeManager.store.get_last_file_index()
        # Indexes of the arrays containing the requested items
        match_indexes = []

        for i in range(1, last_index):
            cur_array = self.storeManager.get_item_at_index(i)
            # Continue if the current array does not match basic criteria
            if cur_array is None or cur_array.previousBlock != 0 or \
               (array_type is not None and cur_array.type is not array_type):
                continue

            if self.array_contains_items(self.read_array_at_index(i), items):
                match_indexes.append(i)
                # Check if we have reached the requested number of matches
                if limit != 0 and len(match_indexes) == limit:
                    return match_indexes
        return match_indexes or None

    def string_ids_for_strings(self, strings):
        """
        Stores the strings in the given list to the array string store file
        and returns a list with the corresponding first indexes

        :param strings: Array of strings to store
        :type strings: list
        :return: Array of string IDs
        :rtype: list
        """
        return map(lambda x: self.stringStoreManager.write_name(x), strings)

    def strings_for_string_ids(self, ids):
        """
        Creates an array of strings from the given list of first indexes

        :param ids: First IDs of strings to retrieve
        :type ids: list
        :return: Array of strings
        :rtype: list
        """
        return map(lambda x: self.stringStoreManager.read_name_at_index(x), ids)

    @staticmethod
    def array_chunks(array, n):
        """
        Break up the given array into chunks of size n

        :param array: Array to break up
        :type array: list
        :param n: Chunk size
        :type n: int
        :return: Broken up array
        :rtype: list
        """
        n = max(1, n)
        return [array[i:i + n] for i in range(0, len(array), n)]

    @staticmethod
    def combine_arrays(array):
        """
        Flattens array chunks into one array, assuming only one level of
        nesting. i.e. [[1, 2, 3, 4], [5, 6, 7, 8], [9]]

        :param array: Array to flatten
        :type array: list
        :return: Flattened array
        :rtype: list
        """
        return list(chain(*array))

    @staticmethod
    def array_contains_items(array, items):
        """
        Check whether the array contains the given items

        :param array: Reference array
        :type array: list
        :param items: Items to check if contained in reference
        :type items: list
        :return: Whether the reference array contains all the items
        :rtype: bool
        """
        return all(map(lambda x: x in array, items))