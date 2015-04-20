from graphene.storage.base.general_store import *
from graphene.storage.base.general_type import *


class GeneralTypeStore(GeneralStore):
    """
    Handles storage of types to files. It stores types using the format
    (inUse, nameId, firstType)
    """

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # '?': boolean
    # 'i': signed int
    STRUCT_FORMAT_STR = "= ? I I"
    ''':type: str'''

    # Size of an individual record (bytes)
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT_STR)
    ''':type: int'''

    # Type stored by this class
    STORAGE_TYPE = GeneralType

    def __init__(self, filename):
        """
        Creates a GeneralTypeStore instance which handles reading/writing to
        the file containing type values

        :param filename: Name of the type store (Nodes or Relationships)
        :type filename: str
        :return: GeneralTypeStore instance for handling GeneralType records
        :rtype: GeneralTypeStore
        """

        # Initialize using generic base class
        super(GeneralTypeStore, self).__init__(filename, self.STRUCT_FORMAT_STR)
        self.FILE_NAME = filename

    def item_from_packed_data(self, index, packed_data):
        """
        Creates a type from the given packed data

        :param index: Index of the type that the packed data belongs to
        :type index: int
        :param packed_data: Packed binary data
        :type packed_data: bytes
        :return: General type from packed data
        :rtype: GeneralType
        """

        # Unpack the data using the GeneralType struct format
        type_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        unpacked_data = type_struct.unpack(packed_data)

        # Get the node components
        in_use = unpacked_data[0]
        name_id = unpacked_data[1]
        first_type = unpacked_data[2]

        # Empty data, deleted item
        if in_use is False and name_id == 0 and first_type == 0:
            return None
        # Create a general type record with these components
        else:
            return GeneralType(index, in_use, name_id, first_type)

    def packed_data_from_item(self, item):
        """
        Creates packed data with GeneralType structure to be written to file

        :param item: GeneralType to convert into packed data
        :type item: GeneralType
        :return: Packed data
        :rtype: bytes
        """
        # Pack the node into a struct with the order (inUse, nameId, firstType)
        node_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        packed_data = node_struct.pack(item.inUse, item.nameId, item.firstType)

        return packed_data

    def empty_struct_data(self):
        """
        Creates a packed struct of 0s

        :return: Packed class struct of 0s
        :rtype: bytes
        """
        empty_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        packed_data = empty_struct.pack(0, 0, 0)
        return packed_data
