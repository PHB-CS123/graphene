import struct

from graphene.storage.base.general_store import *
from graphene.storage.base.string import *


class StringStore(GeneralStore):
    """
    Handles storage of names to a file. It stores names using the format:
    (inUse, previous, length, next, data)
    Everything except data is stored using a struct, while the data (string)
    is stored as is.
    """

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # '?': boolean
    # 'I': unsigned int
    HEADER_STRUCT_FORMAT_STR = "= ? I I I"
    ''':type str'''

    # Size of the header struct (bytes)
    HEADER_SIZE = struct.calcsize(HEADER_STRUCT_FORMAT_STR)
    ''':type int'''

    # Character used to pad the string block
    PAD_CHAR = "\0"
    ''':type str'''

    # Type stored by this class
    STORAGE_TYPE = String

    def __init__(self, filename, block_size=10):
        """
        Creates a StringStore instance which handles reading/writing to the
        file containing string values

        :param filename: Name of file where names are stored
        :type filename: str
        :param block_size: Maximum size of string block
        :type block_size: int
        :return: String store instance for handling string records
        :rtype: StringStore
        """
        # Store the given block size
        self.blockSize = block_size

        # Size of record will be the size of the header and the block itself
        record_size = self.HEADER_SIZE + block_size

        # Initialize using generic base class
        super(StringStore, self).__init__(filename, record_size)

    def write_item(self, item):
        """
        Writes the given string data to the store file

        :param item: String data to write
        :type item: String
        :return: Nothing
        :rtype: None
        """
        # Check that the length of the string is not larger than the block size
        if len(item.string) > self.blockSize:
            raise ValueError("String string to store cannot be larger than the "
                             "block size")

        super(StringStore, self).write_item(item)

    def item_from_packed_data(self, index, packed_data):
        """
        Creates a string type from the given packed data

        :param index: Index of the string that the packed data belongs to
        :type index: int
        :param packed_data: Packed data containing the header and string
        :type packed_data: bytes
        :return: String type from index and packed data
        :rtype: String
        """
        # Split the packed data into header and block
        header_data = packed_data[:self.HEADER_SIZE]
        block_data = packed_data[self.HEADER_SIZE:]

        # Unpack the header data using the header struct format
        header_struct = struct.Struct(self.HEADER_STRUCT_FORMAT_STR)
        unpacked_data = header_struct.unpack(header_data)

        # Get the string components
        in_use = unpacked_data[0]
        prev_block = unpacked_data[1]
        length = unpacked_data[2]
        next_block = unpacked_data[3]

        # Empty data, deleted item
        if in_use is False and prev_block == 0 and length == 0 and \
           next_block == 0:
            return None

        # Unpad the given string string
        name_string = self.unpad_string(block_data)

        # Create a string record with these components
        return String(index, in_use, prev_block, length, next_block, name_string)

    def packed_data_from_item(self, item):
        """
        Creates packed data containing header and the corresponding string

        :param item: Item to convert into packed data
        :type item: String
        :return: Packed data
        :rtype: tuple
        """

        # Pack the header parts into a struct with the order:
        # (inUse, previousBlock, length, nextBlock)
        header_struct = struct.Struct(self.HEADER_STRUCT_FORMAT_STR)
        packed_data = header_struct.pack(item.inUse,
                                         item.previousBlock,
                                         item.length,
                                         item.nextBlock)
        # Pad the string to store with enough null bytes to fill the block
        padded_name = self.pad_string(item.string)

        return packed_data + bytes(padded_name)

    def pad_string(self, string):
        """
        Pads the given string with blockSize - len(string) PAD_CHARs

        :param string: String to pad
        :type string: str
        :return: Padded string
        :rtype: str
        """
        return string.ljust(self.blockSize, self.PAD_CHAR)

    def empty_struct_data(self):
        """
        Creates a packed struct of 0s along with a padded block

        :return: Packed struct of zeros with null padded block
        :rtype: bytes
        """
        return self.empty_header_data() + bytes(self.pad_string(''))

    @classmethod
    def unpad_string(cls, string):
        """
        Removes the padding from the given string

        :param string: Padded String
        :type string: str
        :return: Unpadded string
        :rtype: str
        """
        return string.rstrip(cls.PAD_CHAR)

    @classmethod
    def empty_header_data(cls):
        """
        Creates a packed struct of 0s

        :return: Packed class struct of 0s
        """
        empty_struct = struct.Struct(cls.HEADER_STRUCT_FORMAT_STR)
        packed_data = empty_struct.pack(0, 0, 0, 0)
        return packed_data
