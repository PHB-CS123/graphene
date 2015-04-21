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
        first_index = block.index

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
            block = self.storeManager.create_item(**kwargs)
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
            next_index = next_block.nextBlock
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

    def find_name(self, name):
        """
        Finds the starting index of the given name

        :param name: Name to look for
        :type name: str
        :return: Starting index of name
        :rtype: int
        """
        last_index = self.storeManager.store.get_last_file_index()
        for idx in range(1, last_index):
            cur_name = self.storeManager.get_item_at_index(idx)
            if cur_name.previousBlock == 0 and \
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
