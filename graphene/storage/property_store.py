import struct

from graphene.storage.graphene_store import *
from graphene.storage.property import *


class PropertyStore:
    """
    Handles storage of properties to a file. It stores the properties using
    the format:
    (inUse, type, keyIndexId, propBlockId, prevPropId, nextPropId)
    """

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # '?': boolean
    # 'I': unsigned int
    # 'Q': unsigned long long
    STRUCT_FORMAT_STR = "= ? I I Q I I"
    ''':type: str'''

    # Size of an individual record (bytes)
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT_STR)
    ''':type: int'''

    # Name of PropertyStore File
    FILE_NAME = "graphenestore.propertystore.db"
    ''':type: str'''

    def __init__(self):
        """
        Creates a PropertyStore instance which handles reading/writing to
        the file containing property values

        :return: PropertyStore instance for handling property records
        :rtype: PropertyStore
        """
        graphenestore = GrapheneStore()
        # Get the path of the file
        file_path = graphenestore.datafilesDir + self.FILE_NAME
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
            raise IOError("ERROR: unable to open PropertyStore file: " +
                          file_path)

    def pad_file_header(self):
        """
        Called when the PropertyStore file is first created, pads the
        PropertyStore file with 25 bytes of 0s

        :return: Nothing
        :rtype: None
        """
        # Create a packed struct of 0s
        packed_data = self.empty_struct_data()
        # File pointer should be at 0, no need to seek
        self.storeFile.write(packed_data)

    def property_at_index(self, index):
        """
        Finds the property with the given property index

        :param index: Index of property
        :type index: int
        :return: Property with given index
        :rtype: Property
        """
        if index == 0:
            raise ValueError("Property cannot be read from index 0")

        file_offset = index * self.RECORD_SIZE

        # Seek to the calculated offset
        self.storeFile.seek(file_offset)

        # Get the packed data from the file
        packed_data = self.storeFile.read(self.RECORD_SIZE)

        # This occurs when we've reached the end of the file.
        if packed_data == '':
            return None

        return self.property_from_packed_data(index, packed_data)

    def write_property(self, db_property):
        """
        Writes the given property to the PropertyStore file

        :param db_property: Property to write
        :type db_property: Property
        :return: Nothing
        :rtype: None
        """
        # Pack the property data
        packed_data = self.packed_data_from_property(db_property)
        # Write the packed data to the property index
        self.write_to_index_packed_data(db_property.index, packed_data)

    def delete_property(self, db_property):
        """
        Deletes the given property from the PropertyStore

        :param db_property: Property to delete
        :type db_property: Property
        :return: Nothing
        :rtype: None
        """
        self.delete_property_at_index(db_property.index)


    def delete_property_at_index(self, index):
        """
        Deletes the property at the given index from the PropertyStore

        :param index: Index of the property
        :type index: int
        :return: Nothing
        :rtype: None
        """
        # Get an empty struct to zero-out the data
        empty_struct = self.empty_struct_data()
        # Write the zeroes to the file
        self.write_to_index_packed_data(index, empty_struct)

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
            raise ValueError("Property cannot be written to index 0")

        file_offset = index * self.RECORD_SIZE

        # Seek to the calculated offset and write the data
        self.storeFile.seek(file_offset)
        self.storeFile.write(packed_data)

    def __del__(self):
        """
        Closes the PropertyStore file

        :return: Nothing
        :rtype: None
        """
        self.storeFile.close()

    @classmethod
    def property_from_packed_data(cls, index, packed_data):
        """
        Creates a property from the given packed data

        :param index: Index of the property the packed data belongs to
        :type index: int
        :param packed_data: Packed binary data
        :return: Property from packed data
        :rtype: Property
        """

        # Unpack the data using the property struct format
        property_struct = struct.Struct(cls.STRUCT_FORMAT_STR)
        unpacked_data = property_struct.unpack(packed_data)

        # Get the property components
        in_use = unpacked_data[0]
        prop_type = Property.PropertyType(unpacked_data[1])
        key_index_id = unpacked_data[2]
        prop_block_id = unpacked_data[3]
        prev_prop_id = unpacked_data[4]
        next_prop_id = unpacked_data[5]

        # Create a property record with these components
        return Property(index, in_use, prop_type, key_index_id,
                        prop_block_id, prev_prop_id, next_prop_id)

    @classmethod
    def packed_data_from_property(cls, db_property):
        """
        Creates packed data with the property structure to be written out

        :param db_property: Property to convert into packed data
        :type db_property: Property
        :return: Packed data
        """

        # Pack the property into a struct with the order
        # (inUse, type, keyIndexId, propBlockId, prevPropId, nextPropId)
        property_struct = struct.Struct(cls.STRUCT_FORMAT_STR)

        packed_data = property_struct.pack(db_property.inUse,
                                           db_property.type.value,
                                           db_property.keyIndexId,
                                           db_property.propBlockId,
                                           db_property.prevPropId,
                                           db_property.nextPropId)
        return packed_data

    @classmethod
    def empty_struct_data(cls):
        """
        Creates a packed struct of 0s

        :return: Packed class struct of 0s
        """
        empty_struct = struct.Struct(cls.STRUCT_FORMAT_STR)
        packed_data = empty_struct.pack(0, 0, 0, 0, 0, 0)
        return packed_data
