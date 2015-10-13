import logging

from graphene.storage.base.string_store import *
from graphene.storage.intermediate.general_store_manager import *


class StringManager(object):
    """
    Handles common reading/writing operations for variable-length strings
    """

    def __init__(self, filename, block_size=10):
        """
        Creates a StringManager instance which handles reading/writing
        variable-length strings (ASCII or Unicode)

        :param filename: Name of file where strings will be read/written to
        :type filename: str
        :param block_size: Length of string block
        :type block_size: int
        :return: String manager instance to handle general reading/writing
                 operations
        :rtype: StringManager
        """
        # Size of string blocks
        self.blockSize = block_size
        # Create a manager for the string store
        self.storeManager = GeneralStoreManager(StringStore(filename, block_size))
        import pytest
        pytest.set_trace()  # Check class name for logger
        self.logger = logging.getLogger(self.__class__.__name__)

    def __del__(self):
        del self.storeManager

    def write_string(self, string):
        """
        Write the given variable-length string to the string store

        :param string: String to write
        :type string: str
        :return: Starting index of the stored string
        :rtype: int
        """
        # Encode the given string to store
        string = self.encode(string)
        # Get parts of string (separated based on the block size)
        string_parts = self.split_string(string)
        # Number of parts
        length = len(string_parts)
        # Get IDs to store the blocks into
        ids = self.storeManager.get_indexes(length)

        # TODO: refactor length to amount
        # Block of length 1
        if length == 1:
            kwargs = {'in_use': False,
                      'previous_block': 0,
                      'length': length,
                      'next_block': 0,
                      'string': string_parts[0]}
        else:
            kwargs = {'in_use': False,
                      'previous_block': 0,
                      'length': length,
                      'next_block': ids[1],
                      'string': string_parts[0]}

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
                          'string': string_parts[i]}
            # Create kwargs for middle block
            else:
                kwargs = {'in_use': False,
                          'previous_block': ids[i - 1],
                          'length': length,
                          'next_block': ids[i + 1],
                          'string': string_parts[i]}
            # Create next block
            self.storeManager.create_item(ids[i], **kwargs)
        # Return the first index of the string in the store
        return first_index

    def read_string_at_index(self, index):
        """
        Reads the string at the given index (coalescing the string blocks)

        :param index: Starting index of the string
        :type index: int
        :return: String at the index
        :rtype: str
        """
        # Create empty list where the string strings will be stored
        strings = []
        # The block index will be 0 when there are no more string blocks
        while index != 0:
            # Get string block
            string_block = self.storeManager.get_item_at_index(index)
            # Check if either the string was deleted, or the linked list
            # was broken (only part of a block was deleted)
            if string_block is None:
                return None
            elif string_block == EOF:
                self.logger.warn("Corrupted data, unexpected EOF.")
                return EOF
            # Add the next block string to the list
            strings.append(string_block.string)
            # Update index with the index of the next block
            index = string_block.nextBlock
        # Done, combine the strings
        combined_strings = self.combine_strings(strings)
        # Decode the combined strings and return them
        return self.decode(combined_strings)

    def delete_string_at_index(self, index):
        """
        Deletes the string at the given index

        :param index: Index of string to delete
        :type index: int
        :return: Whether the delete succeeded
        :rtype: bool
        """
        # Store the starting index to check if deletion is
        # starting from beginning of linked list
        start_index = index
        # Iterate until we reach the end of the list
        while index != 0:
            # Get current string block
            string_block = self.storeManager.get_item_at_index(index)
            # Check if either the string was deleted, or the linked list
            # was broken (only part of a block was deleted)
            if string_block is None or string_block is EOF:
                return False
            # Make sure that deletion is starting from start of the linked list
            elif index == start_index and string_block.previousBlock != 0:
                raise IndexError("Cannot begin deletion from non-start index")
            # Get the next index
            next_index = string_block.nextBlock
            # Delete the current block
            self.storeManager.delete_item_at_index(index)
            # Update index to the next index
            index = next_index
        return True

    def update_string_at_index(self, index, new_string):
        """
        Updates the string at the given index

        :param index: Index of original string
        :type index: int
        :param new_string: New string to place at the starting index
        :type new_string: str
        :return: Nothing
        :rtype: None
        """
        # Get parts of string (separated based on the block size)
        string_parts = self.split_string(new_string)
        # Number of parts
        new_length = len(string_parts)

        # Get first string block
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
                      'string': string_parts[0]}
        else:
            kwargs = {'in_use': False,
                      'previous_block': 0,
                      'length': new_length,
                      'next_block': next_id,
                      'string': string_parts[0]}

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
                          'string': string_parts[i]}
            # Create kwargs for middle block
            else:
                kwargs = {'in_use': False,
                          'previous_block': prev_id,
                          'length': new_length,
                          'next_block': next_id,
                          'string': string_parts[i]}
            # Create next block
            self.storeManager.create_item(cur_id, **kwargs)

        # Last item in linked list, but items remain from old string
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
        # Get first string block, set its previousBlock so 0, and
        # write it so interface deletion can be used
        first_block = self.storeManager.get_item_at_index(index)
        first_block.previousBlock = 0
        self.storeManager.write_item(first_block)
        # Delete the items starting with the first item
        self.delete_string_at_index(index)

    def split_string(self, string):
        """
        Splits the given string based on the blockSize

        :param string: String to split
        :type string: str
        :return: List of split sub-strings in order given
        :rtype: list
        """
        # Empty string, return an array with the empty string to store
        if not string:
            return [""]
        return [string[i:i + self.blockSize]
                for i in range(0, len(string), self.blockSize)]

    def find_string(self, string):
        """
        Finds the starting index of the given string.
        Complexity: O(|file|)

        :param string: String to look for
        :type string: str
        :return: Starting index of string
        :rtype: int
        """
        # Last index in the string store file
        last_index = self.storeManager.store.get_last_file_index()
        for idx in range(1, last_index):
            cur_string = self.storeManager.get_item_at_index(idx)
            if cur_string is not None and cur_string.previousBlock == 0 and \
               self.read_string_at_index(idx) == string:
                return idx
        return None

    def find_strings(self, strings):
        """
        Finds the starting indexes of the given strings, allows for only one
        file scan for strings. Complexity: O(|strings|^|file|).
        Do not use if the file contains duplicates

        :param strings: Strings to find starting indexes for
        :type strings: list
        :return: List with indexes for property strings at corresponding indexes
        :rtype: list
        """
        if not strings:
            return None
        strings_amt = len(strings)
        found_amt = 0
        indexes = [0] * strings_amt

        # Last index in the string store file
        last_index = self.storeManager.store.get_last_file_index()
        for idx in range(1, last_index):
            cur_string_part = self.storeManager.get_item_at_index(idx)
            # If valid index, check if strings is one of the strings
            if cur_string_part is not None and cur_string_part.previousBlock == 0:
                cur_string = self.read_string_at_index(idx)
                for (i, string) in enumerate(strings):
                    # TODO: optimize to skip already found strings
                    # String matches
                    if string == cur_string:
                        indexes[i] = idx
                        found_amt += 1
            # Terminate if all strings are found
            if strings_amt == found_amt:
                break
        return indexes

    # TODO: write find_string_mult and find_strings_mult for multiple strings

    @abc.abstractmethod
    def encode(self, string):
        """
        Encodes the given string (needed for unicode)

        :param string: String to encode
        :type string: str
        :return: Encoded string
        :rtype: str
        """
        raise NotImplementedError

    @abc.abstractmethod
    def decode(self, string):
        """
        Decodes the given encoded full string block (needed for unicode)

        :param string: String to decode
        :type string: str
        :return: Decoded string
        :rtype: str
        """
        raise NotImplementedError

    @staticmethod
    def combine_strings(strings):
        """
        Combines the given string blocks

        :param strings: String blocks to combine
        :type strings: list
        :return: Joined string
        :rtype: str
        """
        return "".join(strings)
