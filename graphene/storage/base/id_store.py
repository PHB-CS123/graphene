import struct

from graphene.storage.base.graphene_store import *


class IdStore:
    """
    Handles ID recycling by keeping track of available storage indexes for
    files. File does not have a header.
    """

    # Format string used to compact these values
    # 'I': unsigned int
    INT_FORMAT_STR = "I"
    ''':type: str'''
    # '=': native byte order representation, standard size, no alignment
    ENDIAN_FORMAT_STR = "= "
    ''':type: str'''
    # Complete struct format string
    STRUCT_FORMAT_STR = ENDIAN_FORMAT_STR + INT_FORMAT_STR
    ''':type: str'''

    # Size of an individual record (bytes)
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT_STR)
    ''':type: int'''

    # Return value when no ID is available
    NO_ID = -1
    ''':type: int'''

    # Type stored by this class
    STORAGE_TYPE = int

    def __init__(self, filename):
        """
        Creates an IdStore instance which handles reading/writing to the
        file containing recycled ID values.

        :param filename: Filename to write to. The filename should be the name
                         of the graphene store that the IdStore is for, along
                         with a .id extension
        :type filename: str
        :return: ID store instance for handling recycled IDs
        :rtype: IdStore
        """
        graphenestore = GrapheneStore()
        # Get the path of the file
        file_path = graphenestore.datafilesDir + filename

        # Initialize a next ID variable to prevent multiple reads when peeking.
        # If it is 0, then no nextID has been loaded
        self.nextID = 0

        try:
            # If the file exists, simply open it
            if os.path.isfile(file_path):
                self.storeFile = open(file_path, "r+b")
            else:
                # Create the file
                open(file_path, "w+").close()
                # Open it so that it can be read/written
                self.storeFile = open(file_path, "r+b")
        except IOError:
            raise IOError("ERROR: unable to open IdStore file: " + file_path)

    def __del__(self):
        self.storeFile.close()

    def count(self):
        """
        Get the number of ids

        :return: Number of IDs
        :rtype: int
        """
        return self.get_file_size() / self.RECORD_SIZE

    def clear(self):
        """
        Removes all ids from the IdStore

        :return: Nothing
        :rtype: None
        """
        self.write_all_ids([])

    def get_file_size(self):
        """
        Get the size of the currently open file

        :return: Size of the file currently open (bytes)
        :rtype: long
        """
        # Seek to the end of the file
        self.storeFile.seek(0, os.SEEK_END)

        return self.storeFile.tell()

    def store_id(self, id_value):
        """
        Stores the given ID into the IdStore file

        :param id_value: Id to store
        :type id_value: int
        :return: Nothing
        :rtype: None
        """
        assert id_value != 0, "Nothing should ever be stored at index 0"
        # Seek to the end of the file
        self.storeFile.seek(0, os.SEEK_END)
        # Pack the given ID
        packed_id = struct.Struct(self.STRUCT_FORMAT_STR).pack(id_value)
        # Write the packed ID
        self.storeFile.write(packed_id)

    def get_id(self):
        """
        Gets an ID from the end of the IdStore file. If no ID is available,
        returns NO_ID.

        :return: Available recycled ID
        :rtype: int
        """
        # Try to seek to RECORD_SIZE bytes before the end of the file
        try:
            self.storeFile.seek(-self.RECORD_SIZE, os.SEEK_END)
        # If an IOError is thrown, the file does not have any IDs
        except IOError:
            return self.NO_ID

        # Create struct with the IdStore format string
        id_struct = struct.Struct(self.STRUCT_FORMAT_STR)

        # Read the ID since the seek succeeded
        id_value = id_struct.unpack(self.storeFile.read(self.RECORD_SIZE))[0]

        # Seek back to the position where the ID was read from
        self.storeFile.seek(-self.RECORD_SIZE, os.SEEK_END)
        # Truncate the file from this point on; the ID is no longer available
        self.storeFile.truncate()

        return id_value

    def get_all_ids(self):
        """
        Gets all the IDs from the file. Used for truncation and defragmentation

        :return: List of IDs
        :rtype: list
        """
        # Get the size of the file
        amt_ids = self.get_file_size() / self.RECORD_SIZE
        # No IDs available
        if amt_ids == 0:
            return None
        else:
            # Seek to begining of file
            self.storeFile.seek(0, os.SEEK_SET)
            f_str = self.ENDIAN_FORMAT_STR + str(amt_ids) + self.INT_FORMAT_STR
            ids_struct = struct.Struct(f_str)
            ids = ids_struct.unpack(
                self.storeFile.read(amt_ids * self.RECORD_SIZE))
            return list(ids)

    def write_all_ids(self, ids):
        """
        Overwrites the current ID file with the given IDs

        :param ids: IDs to overwrite file with
        :type ids: list
        :return: Nothing
        :rtype: None
        """
        # Get the existing filename
        file_name = self.storeFile.name
        try:
            # Overwrite the old file
            self.storeFile = open(file_name, "w")

            # Write the new IDs
            f_str = self.ENDIAN_FORMAT_STR + str(len(ids)) + self.INT_FORMAT_STR
            ids_struct = struct.Struct(f_str)
            ids_packed = ids_struct.pack(*ids)
            self.storeFile.write(ids_packed)
            self.storeFile.close()

            # Re-open it so that it can be read/written
            self.storeFile = open(file_name, "r+b")
        except IOError:
            raise IOError("ERROR: unable to open IdStore file: " + file_name)
