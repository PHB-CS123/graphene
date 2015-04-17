from graphene.storage.general_store import *
from graphene.storage.property import *


class PropertyStore(GeneralStore):
    """
    Handles storage of properties to a file. It stores the properties using
    the format:
    (inUse, type, keyIndexId, propBlockId, prevPropId, nextPropId)
    """

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # '?': boolean
    # 'i': signed int
    # 'Q': unsigned long long
    # TODO: determine how to handle signed/unsigned long long for all data types
    STRUCT_FORMAT_STR = "= ? i i Q i i"
    ''':type: str'''

    # Size of an individual record (bytes)
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT_STR)
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

        # Initialize using generic base class
        super(PropertyStore, self).__init__(self.FILE_NAME,
                                            self.STRUCT_FORMAT_STR)

    def item_from_packed_data(self, index, packed_data):
        """
        Creates a property from the given packed data

        :param index: Index of the property the packed data belongs to
        :type index: int
        :param packed_data: Packed binary data
        :return: Property from packed data
        :rtype: Property
        """

        # Unpack the data using the property struct format
        property_struct = struct.Struct(self.STRUCT_FORMAT_STR)
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

    def packed_data_from_item(self, db_property):
        """
        Creates packed data with the property structure to be written out

        :param db_property: Property to convert into packed data
        :type db_property: Property
        :return: Packed data
        """

        # Pack the property into a struct with the order
        # (inUse, type, keyIndexId, propBlockId, prevPropId, nextPropId)
        property_struct = struct.Struct(self.STRUCT_FORMAT_STR)

        packed_data = property_struct.pack(db_property.inUse,
                                           db_property.type.value,
                                           db_property.keyIndexId,
                                           db_property.propBlockId,
                                           db_property.prevPropId,
                                           db_property.nextPropId)
        return packed_data

    def empty_struct_data(self):
        """
        Creates a packed struct of 0s

        :return: Packed class struct of 0s
        """
        empty_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        packed_data = empty_struct.pack(0, 0, 0, 0, 0, 0)
        return packed_data
