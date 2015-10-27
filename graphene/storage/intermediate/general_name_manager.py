from graphene.storage.intermediate.string_manager import *


class GeneralNameManager(StringManager):
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
        super(GeneralNameManager, self).__init__(filename, block_size)

    def __del__(self):
        del self.storeManager

    def encode(self, string):
        # ASCII strings don't need encoding and can be written as-is
        return string

    def decode(self, string):
        # ASCII strings don't need decoding and can be written as-is
        return string
