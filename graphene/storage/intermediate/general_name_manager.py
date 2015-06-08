from graphene.storage.base.name_store import *
from graphene.storage.intermediate.general_store_manager import *

import logging


class GeneralNameManager:
    """
    Handles reading/writing variable-length names (ASCII strings)
    """

    def __init__(self, filename, block_size=10):
        """
        Creates a GeneralNameManager instance which handles reading/writing
        variable-length names (ASCII strings)

        :param filename: Name of file where names will be read/written to
        :type filename: str
        :param block_size: Length of string block
        :type block_size: int
        :return: Name manager instance to handle reading/writing names
        :rtype: GeneralNameManager
        """
        # Size of name blocks
        self.blockSize = block_size
        # Create a manager for the name store
        self.storeManager = GeneralStoreManager(NameStore(filename, block_size))
        self.logger = logging.getLogger(self.__class__.__name__)

    def __del__(self):
        del self.storeManager

    def write_name(self, name):
        """
        Write the given variable-length name to the name store

        :param name: Name to write
        :type name: str
        :return: Starting index of the stored name
        :rtype: int
        """
        # Get parts of name (separated based on the block size)
        name_parts = self.split_name(name)
        # Number of parts
        length = len(name_parts)
        # Get IDs to store the blocks into
        ids = self.storeManager.get_indexes(length)

        # TODO: refactor length to amount
        # Block of length 1
        if length == 1:
            kwargs = {'in_use': False,
                      'previous_block': 0,
                      'length': length,
                      'next_block': 0,
                      'name': name_parts[0]}
        else:
            kwargs = {'in_use': False,
                      'previous_block': 0,
                      'length': length,
                      'next_block': ids[1],
                      'name': name_parts[0]}

        # Create first block using kwargs
        self.storeManager.create_item(ids[0], **kwargs)
        # First index in linked list
        first_index = ids[0]

        # Create rest of linked list
        for i in range(1, length):
            # Last item in linked list
            if i == length - 1:
                kwargs = {'in_use': False,
                          'previous_block': ids[i - 1],
                          'length': length,
                          'next_block': 0,
                          'name': name_parts[i]}
            # Create kwargs for middle block
            else:
                kwargs = {'in_use': False,
                          'previous_block': ids[i - 1],
                          'length': length,
                          'next_block': ids[i + 1],
                          'name': name_parts[i]}
            # Create next block
            self.storeManager.create_item(ids[i], **kwargs)
        # Return the first index of the name in the store
        return first_index

    def read_name_at_index(self, index):
        """
        Reads the name at the given index (coalescing the name blocks)

        :param index: Starting index of the name
        :type index: int
        :return: Name at the index
        :rtype: str
        """
        # Create empty list where the name strings will be stored
        names = []
        # The block index will be 0 when there are no more name blocks
        while index != 0:
            # Get name block
            name_block = self.storeManager.get_item_at_index(index)
            # Check if either the name was deleted, or the linked list
            # was broken (only part of a block was deleted)
            if name_block is None:
                return None
            elif name_block == EOF:
                self.logger.warn("Corrupted data, unexpected EOF.")
                return EOF
            # Add the next block name to the list
            names.append(name_block.name)
            # Update index with the index of the next block
            index = name_block.nextBlock
        # Done, combine the name strings
        return self.combine_names(names)

    def delete_name_at_index(self, index):
        """
        Deletes the name at the given index

        :param index: Index of name to delete
        :type index: int
        :return: Whether the delete succeeded
        :rtype: bool
        """
        # Store the starting index to check if deletion is
        # starting from beginning of linked list
        start_index = index
        # Iterate until we reach the end of the list
        while index != 0:
            # Get current name block
            name_block = self.storeManager.get_item_at_index(index)
            # Check if either the name was deleted, or the linked list
            # was broken (only part of a block was deleted)
            if name_block is None or name_block is EOF:
                return False
            # Make sure that deletion is starting from start of the linked list
            elif index == start_index and name_block.previousBlock != 0:
                raise IndexError("Cannot begin deletion from non-start index")
            # Get the next index
            next_index = name_block.nextBlock
            # Delete the current block
            self.storeManager.delete_item_at_index(index)
            # Update index to the next index
            index = next_index
        return True

    def update_name_at_index(self, index, new_name):
        """
        Updates the name at the given index

        :param index: Index of original name
        :type index: int
        :param new_name: New name to place at the starting index
        :type new_name: str
        :return: Nothing
        :rtype: None
        """
        # Get parts of name (separated based on the block size)
        name_parts = self.split_name(new_name)
        # Number of parts
        new_length = len(name_parts)

        # Get first name block
        cur_block = self.storeManager.get_item_at_index(index)
        # IDs available
        old_length = cur_block.length

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

        # Block of length 1
        if new_length == 1:
            kwargs = {'in_use': False,
                      'previous_block': 0,
                      'length': new_length,
                      'next_block': 0,
                      'name': name_parts[0]}
        else:
            kwargs = {'in_use': False,
                      'previous_block': 0,
                      'length': new_length,
                      'next_block': next_id,
                      'name': name_parts[0]}

        # Create first block using kwargs
        self.storeManager.create_item(cur_id, **kwargs)

        # Create rest of linked list
        for i in range(1, new_length):
            # Prepare IDs for next block
            prev_id = cur_id
            cur_id = next_id

            # No more blocks and not at end of list (does not need a next_id)
            if no_blocks and i != new_length - 1:
                next_id = ids[next_free_id_idx]
                next_free_id_idx += 1
            # Read the next block in this case
            elif not no_blocks:
                cur_block = self.storeManager.get_item_at_index(cur_id)
                next_id = cur_block.nextBlock
            # else: no_blocks, but i == new_length - 1, so next_id is not needed

            # If this update needs IDs, next block does not exist, and not at
            # the end of the list (which does not need a next_id)
            if (ids is not None) and (next_id == 0) and (i != new_length - 1):
                no_blocks = True
                next_id = ids[next_free_id_idx]
                next_free_id_idx += 1

            # Last item in linked list
            if i == new_length - 1:
                kwargs = {'in_use': False,
                          'previous_block': prev_id,
                          'length': new_length,
                          'next_block': 0,
                          'name': name_parts[i]}
            # Create kwargs for middle block
            else:
                kwargs = {'in_use': False,
                          'previous_block': prev_id,
                          'length': new_length,
                          'next_block': next_id,
                          'name': name_parts[i]}
            # Create next block
            self.storeManager.create_item(cur_id, **kwargs)

        # Last item in linked list, but items remain from old name
        if old_length > new_length:
            self.delete_rest(next_id)

    def delete_rest(self, index):
        """
        PRIVATE METHOD. Deletes the list starting at the given index; does not
        need to be at start of list.

        :param index: Index to start deletion on
        :type index: int
        :return: Nothing
        :rtype: None
        """
        # Get first name block, set its previousBlock so 0, and
        # write it so interface deletion can be used
        first_block = self.storeManager.get_item_at_index(index)
        first_block.previousBlock = 0
        self.storeManager.write_item(first_block)
        # Delete the items starting with the first item
        self.delete_name_at_index(index)

    def split_name(self, name):
        """
        Splits the given name based on the blockSize

        :param name: Name to split
        :type name: str
        :return: List of split sub-strings in order given
        :rtype: list
        """
        # Empty name, return an array with the empty string to store
        if not name:
            return [""]
        return [name[i:i + self.blockSize]
                for i in range(0, len(name), self.blockSize)]

    def find_name(self, name):
        """
        Finds the starting index of the given name.
        Complexity: O(|file|)

        :param name: Name to look for
        :type name: str
        :return: Starting index of name
        :rtype: int
        """
        # Last index in the name store file
        last_index = self.storeManager.store.get_last_file_index()
        for idx in range(1, last_index):
            cur_name = self.storeManager.get_item_at_index(idx)
            if cur_name is not None and cur_name.previousBlock == 0 and \
               self.read_name_at_index(idx) == name:
                return idx
        return None

    def find_names(self, names):
        """
        Finds the starting indexes of the given names, allows for only one
        file scan for names. Complexity: O(|names|^|file|).
        Do not use if the file contains duplicates

        :param names: Names to find starting indexes for
        :type names: list
        :return: List with indexes for property names at corresponding indexes
        :rtype: list
        """
        if not names:
            return None
        names_amt = len(names)
        found_amt = 0
        indexes = [0] * names_amt

        # Last index in the name store file
        last_index = self.storeManager.store.get_last_file_index()
        for idx in range(1, last_index):
            cur_name_part = self.storeManager.get_item_at_index(idx)
            # If valid index, check if names is one of the names
            if cur_name_part is not None and cur_name_part.previousBlock == 0:
                cur_name = self.read_name_at_index(idx)
                for (i, name) in enumerate(names):
                    # TODO: optimize to skip already found names
                    # Name matches
                    if name == cur_name:
                        indexes[i] = idx
                        found_amt += 1
            # Terminate if all names are found
            if names_amt == found_amt:
                break
        return indexes

    # TODO: write find_name_mult and find_names_mult for multiple names

    @staticmethod
    def combine_names(names):
        """
        Combines the given name blocks

        :param names: Name blocks to combine
        :type names: list
        :return: Joined string
        :rtype: str
        """
        return "".join(names)
