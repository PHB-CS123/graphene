import struct

from graphene.storage.base.general_store import *
from graphene.storage.base.general_type_type import *


class GeneralTypeTypeStore(GeneralStore):
    """
    Handles storage of types of Node/Relationship types to file. It stores
    types of types using the format:
    (inUse, typeName, propertyType, nextType)
    """

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # '?': boolean
    # 'I': unsigned int
    STRUCT_FORMAT_STR = "= ? I I I"
    ''':type: str'''

    # Size of an individual record (bytes)
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT_STR)
    ''':type: int'''

    # Type stored by this class
    STORAGE_TYPE = GeneralTypeType

    def __init__(self, filename):
        """
        Creates a GeneralTypeTypeStore instance which handles
        reading/writing to the file containing values of types of a type

        :param filename: Name of the type store (Nodes or Relationships)
        :type filename: str
        :return: Store instance for handling records of types of a type
        :rtype: GeneralTypeTypeStore
        """

        # Initialize using generic base class
        super(GeneralTypeTypeStore, self).__init__(filename, self.RECORD_SIZE)
        self.FILE_NAME = filename

    def item_from_packed_data(self, index, packed_data):
        """
        Creates a type from the given packed data

        :param index: Index of the type that the packed data belongs to
        :type index: int
        :param packed_data: Packed binary data
        :type packed_data: bytes
        :return: General type of type from packed data
        :rtype: GeneralTypeType
        """

        # Unpack the data using the GeneralTypeType struct format
        type_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        unpacked_data = type_struct.unpack(packed_data)

        # Get the node components
        in_use = unpacked_data[0]
        type_name = unpacked_data[1]
        prop_type = unpacked_data[2]
        next_type = unpacked_data[3]

        # Empty data, deleted item
        if in_use is False and type_name == 0 and prop_type == 0 \
           and next_type == 0:
            return None
        # Create a general type of type record with these components
        else:
            return GeneralTypeType(index, in_use, type_name,
                                   Property.PropertyType(prop_type), next_type)

    def packed_data_from_item(self, item):
        """
        Creates packed data with general type of type structure
        to be written to file

        :param item: GeneralTypeType to convert into packed data
        :type item: GeneralTypeType
        :return: Packed data
        :rtype: bytes
        """
        # Pack the node into a struct with the order (inUse, nameId, firstType)
        node_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        packed_data = node_struct.pack(item.inUse, item.typeName,
                                       item.propertyType.value, item.nextType)

        return packed_data

    def empty_struct_data(self):
        """
        Creates a packed struct of 0s

        :return: Packed class struct of 0s
        :rtype: bytes
        """
        empty_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        packed_data = empty_struct.pack(0, 0, 0, 0)
        return packed_data
