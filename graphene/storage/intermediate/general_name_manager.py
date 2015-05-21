from graphene.storage.base.name_store import *
from graphene.storage.intermediate.general_store_manager import *


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
        block = self.storeManager.create_item(ids[0], **kwargs)
        # Write it to the file
        self.storeManager.write_item(block)
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
            block = self.storeManager.create_item(ids[i], **kwargs)
            # Write it to the file
            self.storeManager.write_item(block)

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
                raise EOFError("Corrupted data, unexpected EOF.")
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

    def split_name(self, name):
        """
        Splits the given name based on the blockSize

        :param name: Name to split
        :type name: str
        :return: List of split sub-strings in order given
        :rtype: list
        """
        return [name[i:i + self.blockSize]
                for i in range(0, len(name), self.blockSize)]

    def find_name(self, name):
        """
        Finds the starting index of the given name

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
