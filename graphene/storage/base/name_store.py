import struct

from graphene.storage.base.graphene_store import *
from graphene.storage.base.name import *


class NameStore:
    """
    Handles storage of names to a file. It stores names using the format:
    (inUse, previous, length, next, data). Everything except data is stored
    using a struct, while the data (string) is stored as is.
    """

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # '?': boolean
    # 'i': signed int
    HEADER_STRUCT_FORMAT_STR = "= ? I I I"
    ''':type str'''

    # Size of the header struct (bytes)
    HEADER_SIZE = struct.calcsize(HEADER_STRUCT_FORMAT_STR)
    ''':type str'''

    # Character used to pad the string block
    PAD_CHAR = "\0"

    # Type stored by this class
    STORAGE_TYPE = Name

    def __init__(self, filename, block_size=10):
        """
        Creates a NameStore instance which handles reading/writing to the
        file containing name values

        :param filename: Name of file where names are stored
        :type filename: str
        :param block_size: Maximum size of name block (chars, ASCII encoded)
        :type block_size: int
        :return: Name store instance for handling name records
        :rtype: NameStore
        """
        graphenestore = GrapheneStore()
        # Store the filename TODO: move to base class
        self.filename = filename
        # Get the path of the file
        file_path = graphenestore.datafilesDir + filename

        # Store the size of the data block
        self.blockSize = block_size
        # Total record size
        self.recordSize = self.HEADER_SIZE + block_size

        try:
            # If the file exists, simply open it
            if os.path.isfile(file_path):
                self.storeFile = open(file_path, "r+b")
            else:
                # Create the file
                open(file_path, "w+").close()
                # Open it so that it can be read/written
                self.storeFile = open(file_path, "r+b")
                # Pad its first 9 bytes with 0s
                self.pad_file_header()
        except IOError:
            raise IOError("ERROR: unable to open NameStore file: " +
                          file_path)

    def __del__(self):
        """
        Closes the NameStore file

        :return: Nothing
        :rtype: None
        """
        self.storeFile.close()

    def get_last_file_index(self):
        """
        Get the last index of the current file (used when creating new IDs)

        :return: Last index of current file
        :rtype: int
        """
        # Seek to the end of the file
        self.storeFile.seek(0, os.SEEK_END)

        return self.storeFile.tell() / self.recordSize

    def pad_file_header(self):
        """
        Called when the NameStore file is first created, pads the NameStore
        file with 13 + blockSize bytes

        :return: Nothing
        :rtype: None
        """

        # Create a packed header struct of 0s
        packed_data = self.empty_header_data()
        # File pointer should be at 0, no need to seek
        self.storeFile.write(packed_data)
        # Write an empty string with blockSize empty characters
        self.storeFile.write(bytes(self.pad_string('')))

    def item_at_index(self, index):
        """
        Finds the Name with the given index

        :param index: Index of name
        :type index: int
        :return: Name with given index
        :rtype: Name
        """
        if index == 0:
            raise ValueError("Name cannot be read from index 0")

        # Calculate the offset
        file_offset = index * self.recordSize

        # Seek to the calculated offset
        self.storeFile.seek(file_offset)

        # Get the header from the file
        packed_data_header = self.storeFile.read(self.HEADER_SIZE)
        # Get the padded name from the file
        name_string = self.storeFile.read(self.blockSize)

        return self.item_from_data(index, packed_data_header, name_string)

    def write_item(self, name_data):
        """
        Writes the given name to the NameStore file

        :param name_data: Name data to write
        :type name_data: Name
        :return: Nothing
        :rtype: None
        """
        (header_data, name) = self.data_from_item(name_data)
        self.write_to_index_data(name_data.index, header_data, name)

    def delete_item(self, name_data):
        """
        Deletes the given name data from the NameStore

        :param name_data: Name data to delete
        :type name_data: Name
        :return: Nothing
        :rtype: None
        """
        self.delete_item_at_index(name_data.index)

    def delete_item_at_index(self, index):
        """
        Deletes the name data at the given index from the NameStore

        :param index: Index of the name data
        :type index: int
        :return: Nothing
        :rtype: None
        """
        # Get an empty struct to zero-out the data
        empty_header = self.empty_header_data()
        # Padded empty string
        empty_string = self.pad_string('')
        # Write the zeroes and empty string to the file
        self.write_to_index_data(index, empty_header, empty_string)

    def write_to_index_data(self, index, header_data, name):
        """
        Writes the header data and name string to the given index

        :param index: Index to write to
        :type index: int
        :param header_data: Packed data to write
        :param name: Padded name string to write
        :type name: str
        :return: Nothing
        :rtype: None
        """
        if index == 0:
            raise ValueError("Name cannot be written to index 0")
        elif len(name) > self.blockSize:
            raise ValueError("Name string to store cannot be larger than the "
                             "block size")

        # Calculate the offset
        file_offset = index * self.recordSize

        # Seek to the calculated offset and write the data
        self.storeFile.seek(file_offset)
        self.storeFile.write(header_data)
        self.storeFile.write(bytes(name))

    def data_from_item(self, name_data):
        """
        Creates a tuple containing header packed_data and the corresponding name

        :param name_data: Name to convert into packed data
        :type name_data: Name
        :return: Tuple with packed data and the name string
        :rtype: tuple
        """

        # Pack the header parts into a struct with the order:
        # (inUse, previousBlock, length, nextBlock)
        header_struct = struct.Struct(self.HEADER_STRUCT_FORMAT_STR)
        packed_data = header_struct.pack(name_data.inUse,
                                         name_data.previousBlock,
                                         name_data.length,
                                         name_data.nextBlock)
        # Pad the name to store with enough null bytes to fill the block
        padded_name = self.pad_string(name_data.name)

        return packed_data, padded_name

    def item_from_data(self, index, packed_data_header, name):
        """
        Creates a name type from the given packed header and padded name

        :param index: Index of the name that the packed data belongs to
        :type index: int
        :param packed_data_header: Packed binary data header
        :return: Name type from index, header, and name
        :rtype: Name
        """

        # Unpack the data using the header struct format
        header_struct = struct.Struct(self.HEADER_STRUCT_FORMAT_STR)
        unpacked_data = header_struct.unpack(packed_data_header)

        # Get the name components
        in_use = unpacked_data[0]
        prev_block = unpacked_data[1]
        length = unpacked_data[2]
        next_block = unpacked_data[3]

        # Unpad the given name string
        name_string = self.unpad_string(name)

        # Empty data, deleted item
        if in_use is False and prev_block == 0 and length == 0 and \
           next_block == 0:
            return None
        # Create a name record with these components
        else:
            return Name(index, in_use, prev_block, length, next_block,
                        name_string)

    def pad_string(self, string):
        """
        Pads the given string with blockSize - len(string) PAD_CHARs

        :param string: String to pad
        :type string: str
        :return: Padded string
        :rtype: str
        """
        return string.ljust(self.blockSize, self.PAD_CHAR)

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
