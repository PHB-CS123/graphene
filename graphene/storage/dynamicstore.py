import struct
from enum import Enum

from graphene.storage.graphenestore import *
from graphene.storage.dynamic import *


class DynamicStore:

    class DynamicType(Enum):
        # Undefined type
        undefined = 0
        # String type
        string = 1
        # Array types
        intArray = 2
        longArray = 3
        boolArray = 4
        shortArray = 5
        charArray = 6
        floatArray = 7
        doubleArray = 8
        stringArray = 9

    STRUCT_HEADER = "= ? I I I "
    ''':type str'''

    HEADER_SIZE = struct.calcsize(STRUCT_HEADER)
    ''':type str'''

    def __init__(self, dynamic_type, file_name):
        """
        Creates a DynamicStore instance which handles reading/writing to
        the file containing dynamic values

        :param dynamic_type: Type of dynamic store file
        :type dynamic_type: DynamicType
        :param file_name: Name of dynamic store file
        :type file_name: str
        :return: DynamicStore instance for handling dynamic records
        :rtype: DynamicStore
        """
        graphenestore = GrapheneStore()

        # Store the type of dynamic store
        self.dynamicType = dynamic_type

        # Get the path of the file
        file_path = graphenestore.datafilesDir + file_name
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
            raise IOError("ERROR: unable to open DynamicStore file: " +
                          file_path)

    def pad_file_header(self):
        """
        Called when the DynamicStore file is first created, pads the
        DynamicStore file with 13 bytes of 0s

        :return: Nothing
        :rtype: None
        """
        # Create a packed struct of 0s
        empty_struct = struct.Struct(self.STRUCT_HEADER)
        packed_data = empty_struct.pack(0, 0, 0, 0)
        # File pointer should be at 0, no need to seek
        self.storeFile.write(packed_data)

    def read_header_at_index(self, index):

        file_offset = index * self.HEADER_SIZE
