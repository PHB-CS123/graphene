import struct

from graphene.storage.graphene_store import *


class GeneralStore:

    def __init__(self, filename, struct_format_string):
        graphenestore = GrapheneStore()
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

    def empty_struct_data(self):
        """
        Creates a packed struct of 0s

        :return: Packed class struct of 0s
        """
        empty_struct = struct.Struct(self.structFormatString)
        # Count spaces (excluding leading or trailing) to get data values
        # i.e. "= ? I I I" => 4 data values, 4 spaces. Assuming there is
        # a first character for byte order/size/alignment (@ = < > !)
        data_values = self.structFormatString.strip().count()
        data_values_tuple = data_values * (0,)
        packed_data = empty_struct.pack(data_values_tuple)
        return packed_data