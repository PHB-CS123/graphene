from graphene.storage.base.name_store import *
from graphene.storage.intermediate.general_store_manager import *


class GeneralNameManager:

    def __init__(self, block_size):
        # Size of name blocks
        self.blockSize = block_size
        # Create a manager for the name store
        self.storeManager = GeneralStoreManager(NameStore(block_size))

    def write_name(self, name):
        name_parts = self.split_name(name)
        num_parts = len(name_parts)
        for i, name in enumerate(name_parts):
            self.storeManager.create_item()

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