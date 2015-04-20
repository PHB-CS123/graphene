import struct

from graphene.storage.base.graphene_store import *


class IdStore:
    """
    Handles ID recycling by keeping track of available storage indexes for
    files. File does not have a header.
    """

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # 'i': signed int
    STRUCT_FORMAT_STR = "= I"
    ''':type: str'''

    # Size of an individual record (bytes)
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT_STR)

    # Return value when no ID is available
    NO_ID = -1

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
            raise IOError("ERROR: unable to open IdStore file: " +
                          file_path)

    def store_id(self, id_value):
        """
        Stores the given ID into the IdStore file

        :param id_value: Id to store
        :type id_value: int
        :return: Nothing
        :rtype: None
        """
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

    def peek_id(self):
        """
        Returns the next ID from the file without removing it
        :return: Next Id
        :rtype:
        """