from graphene.storage.intermediate.general_name_manager import *
from graphene.storage.base.array_store import *

from itertools import chain
import logging

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
        self.logger = logging.getLogger(self.__class__.__name__)

    def __del__(self):
        del self.stringStoreManager
        del self.storeManager

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
        # Create an array with string IDs for all the string items
        if array_type == Property.PropertyType.stringArray:
            array = self.string_ids_for_strings(array)

        # Get parts of the array (separated based on the block size and type)
        capacity = ArrayStore.capacity_for_type(array_type, self.blockSize)
        parts = self.split_array(array, capacity)

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
                      'blocks': amt_parts,
                      'next_block': 0,
                      'items': parts[0]}
        else:
            kwargs = {'in_use': False,
                      'array_type': array_type,
                      'previous_block': 0,
                      'amount': len(parts[0]),
                      'blocks': amt_parts,
                      'next_block': ids[1],
                      'items': parts[0]}
        # Create first block using kwargs
        self.storeManager.create_item(ids[0], **kwargs)
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
                          'blocks': amt_parts,
                          'next_block': 0,
                          'items': parts[i]}
            # Create kwargs for middle block
            else:
                kwargs = {'in_use': False,
                          'array_type': array_type,
                          'previous_block': ids[i - 1],
                          'amount': len(parts[i]),
                          'blocks': amt_parts,
                          'next_block': ids[i + 1],
                          'items': parts[i]}
            # Create next block
            self.storeManager.create_item(ids[i], **kwargs)
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
                self.logger.warn("Corrupted data, unexpected EOF.")
                return EOF
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
            # Delete strings if string array
            if array_block.is_string_array():
                self.delete_names_at_indexes(array_block.items)
            # Get the next index
            next_index = array_block.nextBlock
            # Delete the current block
            self.storeManager.delete_item_at_index(index)
            # Update index to the next index
            index = next_index
        return True

    def update_array_at_index(self, index, new_array):
        """
        Updates the array at the given starting index

        :param index: Index of original array
        :type index: int
        :param new_array: New array to store
        :type new_array: list
        :return: Nothing
        :rtype: None
        """
        # Get first array block
        cur_block = self.storeManager.get_item_at_index(index)
        # IDs available
        old_length = cur_block.length
        # Get type of array
        array_type = cur_block.type
        # Whether it's a string array
        is_string_array = cur_block.is_string_array()

        # Get parts of the array (separated based on the block size and type)
        capacity = ArrayStore.capacity_for_type(array_type, self.blockSize)
        array_parts = self.split_array(new_array, capacity)
        # Number of parts
        new_length = len(array_parts)

        # Get IDs to store the remaining blocks into
        if old_length < new_length:
            ids = self.storeManager.get_indexes(new_length - old_length)
        else:
            ids = None

        # Initialize IDs according to first block
        cur_id = cur_block.index
        next_id = cur_block.nextBlock

        # If next ID is 0, then there are no more blocks available
        if next_id == 0 and ids is not None:
            no_blocks = True
            next_free_id_idx = 1
            next_id = ids[0]
        else:
            no_blocks = False
            next_free_id_idx = 0

        # String array, store the name parts
        if is_string_array:
            array_parts[0] = \
                self.update_names_at_indexes(cur_block.items, array_parts[0])

        # Block of length 1
        if new_length == 1:
            kwargs = {'in_use': False,
                      'array_type': array_type,
                      'previous_block': 0,
                      'amount': len(array_parts[0]),
                      'blocks': new_length,
                      'next_block': 0,
                      'items': array_parts[0]}
        else:
            kwargs = {'in_use': False,
                      'array_type': array_type,
                      'previous_block': 0,
                      'amount': len(array_parts[0]),
                      'blocks': new_length,
                      'next_block': next_id,
                      'items': array_parts[0]}

        # Create first block using kwargs
        self.storeManager.create_item(cur_id, **kwargs)

        # Create rest of linked list
        for i in range(1, new_length):
            # Prepare IDs for next block
            prev_id = cur_id
            cur_id = next_id

            block_ids = None
            # No more blocks and not at end of list (does not need a next_id)
            if no_blocks:
                # Next ID is not needed at the end of the list
                if i != new_length - 1:
                    next_id = ids[next_free_id_idx]
                    next_free_id_idx += 1
            # Read the next block in this case
            else:
                cur_block = self.storeManager.get_item_at_index(cur_id)
                next_id = cur_block.nextBlock
                # If string array, get IDs of current block to use for update
                block_ids = cur_block.items if is_string_array else None
            # Update names for string array based on block_ids, if no block ids,
            # create new ids (i.e. no blocks so block_ids will be None)
            if is_string_array:
                array_parts[i] = \
                    self.update_names_at_indexes(block_ids, array_parts[i])

            # If this update needs IDs, next block does not exist, and not at
            # the end of the list (which does not need a next_id)
            if (ids is not None) and (next_id == 0) and (i != new_length - 1):
                no_blocks = True
                next_id = ids[next_free_id_idx]
                next_free_id_idx += 1

            # Last item in linked list
            if i == new_length - 1:
                kwargs = {'in_use': False,
                          'array_type': array_type,
                          'previous_block': prev_id,
                          'amount': len(array_parts[i]),
                          'blocks': new_length,
                          'next_block': 0,
                          'items': array_parts[i]}
            # Create kwargs for middle block
            else:
                kwargs = {'in_use': False,
                          'array_type': array_type,
                          'previous_block': prev_id,
                          'amount': len(array_parts[i]),
                          'blocks': new_length,
                          'next_block': next_id,
                          'items': array_parts[i]}
            # Create next block
            self.storeManager.create_item(cur_id, **kwargs)

        # Last item in linked list, but items remain from old array
        if old_length > new_length:
            self.delete_rest(next_id)  # Handles string deletion as well

    def delete_rest(self, index):
        """
        PRIVATE METHOD. Deletes the list starting at the given index; does not
        need to be at start of list.

        :param index: Index to start deletion on
        :type index: int
        :return: Nothing
        :rtype: None
        """
        # Get first array block, set its previousBlock so 0, and
        # write it so interface deletion can be used
        first_block = self.storeManager.get_item_at_index(index)
        first_block.previousBlock = 0
        self.storeManager.write_item(first_block)
        # Delete the items starting with the first item
        self.delete_array_at_index(index)

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

    def delete_names_at_indexes(self, ids):
        """
        Deletes the names at the given list of first indexes

        :param ids: First IDs of strings to delete
        :type ids: list
        :return: Whether any of the deletes failed
        :rtype: bool
        """
        return all(map(lambda x:
                       self.stringStoreManager.delete_name_at_index(x), ids))

    def update_names_at_indexes(self, ids, new_names):
        """
        Updates the names at the starting indexes with the new names, 3 cases:
        1) len(ids) > len(new_names): Delete ids not used for update, then (3)
        2) len(ids) < len(new_names): Use given IDs, create new strings, done.
        3) len(ids) == len(new_names): Easy case, just use given IDs

        :param ids: Starting indexes of old names
        :type ids: list[int]
        :param new_names: New names to place at these starting indexes
        :type new_names: list[str]
        :return: List of IDs where respective names were stored
        :rtype: list[int]
        """
        # If no IDs are given, default to just creating ids for new names
        if not ids:
            return self.string_ids_for_strings(new_names)

        num_ids = len(ids)
        num_names = len(new_names)
        # Delete extraneous IDs
        if num_ids > num_names:
            self.delete_names_at_indexes(ids[num_names:])
            ids = ids[:num_names]
        # Use IDs given and create new strings in the store for the rest
        elif num_ids < num_names:
            # Names without IDs that need to be stored
            remaining_names = new_names[num_ids:]
            new_names = new_names[:num_ids]
            # Update the names
            map(lambda x, y:
                self.stringStoreManager.update_name_at_index(x, y),
                ids, new_names)
            # Now store the remaining names
            rest_ids = map(lambda x: self.stringStoreManager.write_name(x),
                           remaining_names)
            # Return the updated IDs and the created IDs
            return ids + rest_ids
        # else: len(ids) == len(new_names), perform update for names with ids
        map(lambda x, y:
            self.stringStoreManager.update_name_at_index(x, y), ids, new_names)
        return ids

    @staticmethod
    def split_array(array, n):
        """
        Break up the given array into chunks of size n

        :param array: Array to break up
        :type array: list
        :param n: Chunk size
        :type n: int
        :return: Broken up array
        :rtype: list
        """
        if len(array) == 0:
            return [[]]
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
