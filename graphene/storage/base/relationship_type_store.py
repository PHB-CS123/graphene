from graphene.storage.base.general_store import *
from graphene.storage.base.relationship_type import *


class RelationshipTypeStore(GeneralStore):
    """
    Handles storage of relationship types to a file. Stores types with the
    following format:

      (inUse, typeBlockID)

    where typeBlockID is a pointer to the DynamicStore that stores the
    string name of the type.
    """

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # '?': boolean
    # 'i': signed int
    STRUCT_FORMAT_STR = "= ? I"
    ''':type: str'''

    # Size of an individual record (bytes)
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT_STR)
    ''':type: int'''

    # Name of RelationshipTypeStore File
    FILE_NAME = "graphenestore.relationshiptypestore.db"
    ''':type: str'''

    # Type stored by this class
    STORAGE_TYPE = RelationshipType

    def __init__(self):
        """
        Creates a RelationshipTypeStore instance.

        :return: RelationshipStore instance for handling relationship records
        :rtype: RelationshipStore
        """
        # Initialize using generic base class
        super(RelationshipTypeStore, self).__init__(self.FILE_NAME,
                                                    self.STRUCT_FORMAT_STR)

    def item_from_packed_data(self, index, packed_data):
        """
        Creates a relationship type from the given packed data

        :param index: Index of the relationship type the packed data belongs to
        :type index: int
        :param packed_data: Packed binary data
        :type packed_data: bytes
        :return: Relationship type from packed data
        :rtype: RelationshipType
        """
        # Unpack the data using the relationship type struct format
        relationship_type_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        unpacked_data = relationship_type_struct.unpack(packed_data)

        # Get the relationship type components
        in_use = unpacked_data[0]
        type_block_id = unpacked_data[1]

        if in_use is False and type_block_id == 0:
            return None
        # Create a relationship type with these contents
        else:
            return RelationshipType(index, in_use, type_block_id)

    def packed_data_from_item(self, relationship_type):
        """
        Create packed data with RelationshipType structure to be written.

        :param relationship_type: RelationshipType object to convert.
        :type relationship_type: RelationshipType
        :return: Packed data string.
        """
        relationship_type_struct = struct.Struct(self.STRUCT_FORMAT_STR)

        packed_data = relationship_type_struct.pack(
            relationship_type.inUse, relationship_type.typeBlockId)

        return packed_data

    def empty_struct_data(self):
        """
        Creates a packed struct of 0s

        :return: Packed class struct of 0s
        """
        empty_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        packed_data = empty_struct.pack(0, 0)
        return packed_data