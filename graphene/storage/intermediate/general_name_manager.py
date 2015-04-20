from graphene.storage.base.name_store import *
from graphene.storage.intermediate.general_store_manager import *


class GeneralNameManager:
    """
    Handles handles reading/writing variable-length names (ASCII strings)
    """

    def __init__(self, filename, block_size):
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

        # First block
        kwargs = {'in_use': False,
                  'previous_block': 0,
                  'length': length,
                  'next_block': 0,
                  'name': name_parts[0]}
        # Create first block using kwargs
        next_block = self.storeManager.create_item(**kwargs)
        # First index in linked list
        first_index = next_block.index

        # Create rest of linked list
        for i in range(1, length):
            # Previous block is old next block
            prev_block = next_block
            # Create kwargs for current block
            kwargs = {'in_use': False,
                      'previous_block': prev_block.index,
                      'length': length,
                      'next_block': 0,
                      'name': name_parts[i]}
            # Create next block
            next_block = self.storeManager.create_item(**kwargs)
            # Set the next index of the previous block to point to the new block
            prev_block.next_block = next_block.index
            # Write it back to the file
            self.storeManager.write_item(prev_block)

        # Write the last-created block to the file (next_block is 0)
        self.storeManager.write_item(next_block)
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
        # Get first block from file
        first_name_block = self.storeManager.get_item_at_index(index)
        # Create list with the name at the first block
        names = [first_name_block.name]
        # Index of next block
        next_index = first_name_block.nextBlock
        # The block index will be 0 when there are no more name blocks
        while next_index != 0:
            next_block = self.storeManager.get_item_at_index(next_index)
            # Add the next block name to the list
            names.append(next_block.name)
            # Update index of next block
            next_index = next_block.next
        # Done, combine the name strings
        return self.combine_names(names)

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
