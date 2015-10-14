from graphene.storage.intermediate.string_manager import *


class GeneralStringManager(StringManager):
    """
    Handles reading/writing variable-length strings (Unicode)
    """

    # Default encoding
    ENCODING = "UTF-8"

    def __init__(self, filename, block_size=10):
        """
        Creates a GeneralStringManager instance which handles reading/writing
        variable-length strings (ASCII strings)

        :param filename: Name of file where names will be read/written to
        :type filename: str
        :param block_size: Length of string block
        :type block_size: int
        :return: String manager instance to handle reading/writing strings
        :rtype: GeneralStringManager
        """
        super(GeneralStringManager, self).__init__(filename, block_size)

    def __del__(self):
        del self.storeManager

    def encode(self, string):
        # Encode the string using the default encoding
        return string.encode(self.ENCODING)

    def decode(self, string):
        # Decode the string using the default encoding
        return string.decode(self.ENCODING)
