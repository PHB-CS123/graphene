import struct

from graphene.storage.base.general_store import *
from graphene.storage.base.property import *


class PropertyStore(GeneralStore):
    """
    Handles storage of properties to a file. It stores the properties using
    the format:
    (inUse, type, nameId, prevPropId, nextPropId, propBlockId)
    """

    # Format string used to compact header values
    # '=': native byte order representation, standard size, no alignment
    # '?': boolean
    # 'B': unsigned char
    # 'I': unsigned int
    HEADER_STRUCT_FORMAT_STR = "= ? B I I I "
    ''':type: str'''

    # Size of header
    HEADER_SIZE = struct.calcsize(HEADER_STRUCT_FORMAT_STR)
    ''':type: int'''

    # Format string used to read types other than floats and doubles
    # 'q': signed long long
    REGULAR_FORMAT_STR = "q"
    ''':type: str'''

    # Format string to handle float and double types
    # 'd': double
    LONG_FORMAT_STR = "d"
    ''':type: str'''

    # Size of data block (same whether decimal or non-decimal: 8 bytes)
    BLOCK_SIZE = struct.calcsize(REGULAR_FORMAT_STR)
    ''':type: int'''

    # Name of PropertyStore File
    FILE_NAME = "graphenestore.propertystore.db"
    ''':type: str'''

    # Type stored by this class
    STORAGE_TYPE = Property

    def __init__(self):
        """
        Creates a PropertyStore instance which handles reading/writing to
        the file containing property values

        :return: PropertyStore instance for handling property records
        :rtype: PropertyStore
        """
        # Size of record will be the size of the header and the block itself
        record_size = self.HEADER_SIZE + self.BLOCK_SIZE

        # Initialize using generic base class
        super(PropertyStore, self).__init__(self.FILE_NAME, record_size)

    def item_from_packed_data(self, index, packed_data):
        """
        Creates a property from the given packed data

        :param index: Index of the property the packed data belongs to
        :type index: int
        :param packed_data: Packed binary data
        :type packed_data: bytes
        :return: Property from packed data
        :rtype: Property
        """
        # Split the packed data into header and block
        header_data = packed_data[:self.HEADER_SIZE]
        block_data = packed_data[self.HEADER_SIZE:]

        # Unpack the header data using the header struct format
        header_struct = struct.Struct(self.HEADER_STRUCT_FORMAT_STR)
        unpacked_header_data = header_struct.unpack(header_data)

        # Get the property header components
        in_use = unpacked_header_data[0]
        prop_type = Property.PropertyType(unpacked_header_data[1])
        key_index_id = unpacked_header_data[2]
        prev_prop_id = unpacked_header_data[3]
        next_prop_id = unpacked_header_data[4]

        # Empty data, deleted item
        if in_use is False and prop_type == Property.PropertyType.undefined \
           and key_index_id == 0 and prev_prop_id == 0 and next_prop_id == 0:
            return None

        # Unpack the block data
        prop_block_id = self.value_from_data(prop_type, block_data)

        # Create a property record with these components
        return Property(index, in_use, prop_type, key_index_id,
                        prev_prop_id, next_prop_id, prop_block_id)

    def packed_data_from_item(self, item):
        """
        Creates packed data with the property given

        :param item: Property to convert into packed data
        :type item: Property
        :return: Packed data
        :rtype: bytes
        """
        # Pack the property header into a struct with the order
        # (inUse, type, keyIndexId, prevPropId, nextPropId)
        header_struct = struct.Struct(self.HEADER_STRUCT_FORMAT_STR)
        packed_header = header_struct.pack(item.inUse, item.type.value,
                                           item.nameId, item.prevPropId,
                                           item.nextPropId)
        # Pack the data block
        packed_block = self.value_to_data(item.type, item.propBlockId)
        # Concatenate the two
        return packed_header + packed_block

    def empty_struct_data(self):
        """
        Creates a packed struct of 0s

        :return: Packed struct of 0s
        :rtype: bytes
        """
        empty_struct = struct.Struct(self.HEADER_STRUCT_FORMAT_STR +
                                     self.REGULAR_FORMAT_STR)
        packed_data = empty_struct.pack(0, 0, 0, 0, 0, 0)
        return packed_data

    @classmethod
    def value_from_data(cls, prop_type, packed_data):
        """
        Unpacks the given packed data according to the property type

        :param prop_type: Property type of the value
        :type prop_type: PropertyType
        :param packed_data: Packed data to convert to value
        :type packed_data: bytes
        :return: Value of type prop_type
        """
        # Long values (8 bytes)
        if prop_type is Property.PropertyType.double or \
           prop_type is Property.PropertyType.float:
            decimal_struct = struct.Struct(cls.LONG_FORMAT_STR)
            return decimal_struct.unpack(packed_data)[0]

        # Unpack the general data
        general_struct = struct.Struct(cls.REGULAR_FORMAT_STR)
        general_value = general_struct.unpack(packed_data)[0]

        # Character type stored as ASCII value
        if prop_type is Property.PropertyType.char:
            return unichr(general_value)
        # Convert to boolean value
        elif prop_type is Property.PropertyType.bool:
            return bool(general_value)
        # These general values do not need further processing:
        # int, long, short, or an index to a dynamic store for dynamic types
        else:
            return general_value

    @classmethod
    def value_to_data(cls, prop_type, value):
        """
        Packs the given value using the appropriate struct format string

        :param prop_type: Property type of the value
        :type prop_type: PropertyType
        :param value: Value to pack with the given type
        :return: Packed value
        :rtype: bytes
        """
        # Long values (8 bytes)
        if prop_type is Property.PropertyType.double or \
           prop_type is Property.PropertyType.float:
            decimal_struct = struct.Struct(cls.LONG_FORMAT_STR)
            return decimal_struct.pack(value)

        # Create a struct for the other cases
        general_struct = struct.Struct(cls.REGULAR_FORMAT_STR)

        # Convert character into ASCII value
        if prop_type is Property.PropertyType.char:
            return general_struct.pack(ord(value))
        # Convert boolean value to long
        elif prop_type is Property.PropertyType.bool:
            return general_struct.pack(long(value))
        # These general values do not need further processing:
        # int, long, short, or an index to a dynamic store for dynamic types
        else:
            return general_struct.pack(value)