import struct
import abc

from graphene.storage.base.graphene_store import *


class GeneralStore(object):
    """
    Handles the general storage operations of different types.
    """

    # Used to indicate abstract methods
    __metaclass__ = abc.ABCMeta

    def __init__(self, filename, struct_format_string):
        """
        Creates a GeneralStore instance which handles reading/writing
        to store files for different value types

        :param filename: Name of store file
        :type filename: str
        :param struct_format_string: Format string used to compact values
        :type struct_format_string: str
        :return: GeneralStore instance meant to be sub-classed
        :rtype: GeneralStore
        """
        graphenestore = GrapheneStore()

        # Store the given filename
        self.filename = filename
        # Get the path of the file
        file_path = graphenestore.datafilesDir + filename

        # Store struct information
        self.structFormatString = struct_format_string
        self.recordSize = struct.calcsize(struct_format_string)

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
            raise IOError("ERROR: unable to open file: " + file_path)

    def __del__(self):
        """
        Closes the store file

        :return: Nothing
        :rtype: None
        """
        self.storeFile.close()

    def pad_file_header(self):
        # Create a packed struct of 0s
        packed_data = self.empty_struct_data()
        # File pointer should be at 0, no need to seek
        self.storeFile.write(packed_data)

    def get_last_file_index(self):
        """
        Get the last index of the current file (used when creating new IDs)

        :return: Last index of current file
        :rtype: int
        """
        # Seek to the end of the file
        self.storeFile.seek(0, os.SEEK_END)

        return self.storeFile.tell() / self.recordSize

    def item_at_index(self, index):
        """
        Finds the item with the given index

        :param index: Index of item
        :type index: int
        :return: Item with given index
        """
        if index == 0:
            raise ValueError("Item cannot be read from index 0")

        file_offset = index * self.recordSize

        # Seek to the calculated offset
        self.storeFile.seek(file_offset)

        # Get the packed data from the file
        packed_data = self.storeFile.read(self.recordSize)

        # This occurs when we've reached the end of the file.
        if packed_data == '':
            return None
        else:
            return self.item_from_packed_data(index, packed_data)

    def write_item(self, item):
        """
        Writes the given item to the store file

        :param item: Item to write
        :return: Nothing
        :rtype: None
        """
        # Pack the item data, then write it to the item index
        packed_data = self.packed_data_from_item(item)
        # Write the packed data to the item index
        self.write_to_index_packed_data(item.index, packed_data)

    def write_to_index_packed_data(self, index, packed_data):
        """
        Writes the packed data to the given index

        :param index: Index to write to
        :type index: int
        :param packed_data: Packed data to write
        :return: Nothing
        :rtype: None
        """
        if index == 0:
            raise ValueError("Item cannot be written to index 0")

        file_offset = index * self.recordSize

        # Seek to the calculated offset and write the data
        self.storeFile.seek(file_offset)
        self.storeFile.write(packed_data)

    def delete_item(self, item):
        """
        Deletes the given item from the store

        :param item: Item to delete
        :return: Nothing
        :rtype: None
        """
        self.delete_item_at_index(item.index)

    def delete_item_at_index(self, index):
        """
        Deletes the item at the given index from the store

        :param index: Index of the item
        :type index: int
        :return: Nothing
        :rtype: None
        """
        # Get an empty struct to zero-out the data
        empty_struct = self.empty_struct_data()
        # Write the zeroes to the file
        self.write_to_index_packed_data(index, empty_struct)

    @abc.abstractmethod
    def item_from_packed_data(self, index, packed_data):
        """
        Creates an item from the given packed data

        :param index: Index of the item that the packed data belongs to
        :type index: int
        :param packed_data: Packed binary data
        :type packed_data: bytes
        :return: Item from packed data
        """
        return

    @abc.abstractmethod
    def packed_data_from_item(self, item):
        """
        Abstract method: Creates packed data with struct format string
        to be written to a file

        :param item: Item to convert into packed data
        :return: Packed data
        :rtype: bytes
        """
        return

    @abc.abstractmethod
    def empty_struct_data(self):
        """
        Abstract method: creates packed struct of 0s

        :return: Packed struct of 0s
        :rtype: bytes
        """
        return