from graphene.storage.general_store import *
from graphene.storage.relationship import *


class RelationshipStore(GeneralStore):
    """
    Handles storage of relationships to a file. It stores relationships using
    the format:
    (inUse_direction, firstNode, secondNode, relType, firstPrevRelId,
     firstNextRelId, secondPrevRelId, secondNextRelId, nextPropId)
    """

    class InUseAndDir(Enum):
        undefined = 0
        inUse_rightDir = 1
        inUse_leftDir = 2
        notInUse_rightDir = 3
        notInUse_leftDir = 4

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # 'B': unsigned char
    # 'i': signed int
    STRUCT_FORMAT_STR = "= B I I I I I I I I"
    ''':type: str'''

    # Size of an individual record (bytes)
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT_STR)
    ''':type: int'''

    # Name of RelationshipStore File
    FILE_NAME = "graphenestore.relationshipstore.db"
    ''':type: str'''

    # Type stored by this class
    STORAGE_TYPE = Relationship

    def __init__(self):
        """
        Creates a RelationshipStore instance which handles reading/writing to
        the file containing relationship values

        :return: RelationshipStore instance for handling relationship records
        :rtype: RelationshipStore
        """
        # Initialize using generic base class
        super(RelationshipStore, self).__init__(self.FILE_NAME,
                                                self.STRUCT_FORMAT_STR)

    def item_from_packed_data(self, index, packed_data):
        """
        Creates a relationship from the given packed data

        :param index: Index of the relationship the packed data belongs to
        :type index: int
        :param packed_data: Packed binary data
        :type packed_data: bytes
        :return: Relationship from packed data
        :rtype: Relationship
        """

        # Unpack the data using the relationship struct format
        relationship_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        unpacked_data = relationship_struct.unpack(packed_data)

        # Get the relationship components

        # Get in use and direction from byte, make enum and extract values
        in_use_dir = unpacked_data[0]
        enum = self.InUseAndDir(in_use_dir)
        (in_use, direction) = self.in_use_dir_from_enum(enum)

        # Get rest of components
        first_node_id = unpacked_data[1]
        second_node_id = unpacked_data[2]
        rel_type = unpacked_data[3]
        first_prev_rel_id = unpacked_data[4]
        first_next_rel_id = unpacked_data[5]
        second_prev_rel_id = unpacked_data[6]
        second_next_rel_id = unpacked_data[7]
        prop_id = unpacked_data[8]

        # Create a relationship record with these components
        return Relationship(index, in_use, direction, first_node_id,
                            second_node_id, rel_type, first_prev_rel_id,
                            first_next_rel_id, second_prev_rel_id,
                            second_next_rel_id, prop_id)

    def packed_data_from_item(self, relationship):
        """
        Creates packed data with Relationship structure to be written to a file

        :param relationship: Relationship to convert into packed data
        :type relationship: Relationship
        :return: Packed data
        """

        # Pack the relationship into a struct with the order
        # (inUse_direction, firstNode, secondNode, relType, firstPrevRelId,
        #  firstNextRelId, secondPrevRelId, secondNextRelId, nextPropId)
        relationship_struct = struct.Struct(self.STRUCT_FORMAT_STR)

        # Create enum to combine the in use and direction values
        enum = self.enum_from_in_use_dir(relationship.inUse,
                                         relationship.direction)

        packed_data = relationship_struct.pack(enum.value,
                                               relationship.firstNodeId,
                                               relationship.secondNodeId,
                                               relationship.relType,
                                               relationship.firstPrevRelId,
                                               relationship.firstNextRelId,
                                               relationship.secondPrevRelId,
                                               relationship.secondNextRelId,
                                               relationship.propId)

        return packed_data

    def empty_struct_data(self):
        """
        Creates a packed struct of 0s

        :return: Packed class struct of 0s
        """
        empty_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        packed_data = empty_struct.pack(0, 0, 0, 0, 0, 0, 0, 0, 0)
        return packed_data

    @classmethod
    def in_use_dir_from_enum(cls, enum):
        """
        Get the in use and direction from the given enum which contains both

        :param enum: Enum containing both values
        :type enum: InUseAndDir
        :return: Tuple (in_use, direction)
        :rtype: tuple
        """
        if enum == cls.InUseAndDir.inUse_leftDir:
            return True, Relationship.Direction.left
        elif enum == cls.InUseAndDir.inUse_rightDir:
            return True, Relationship.Direction.right
        elif enum == cls.InUseAndDir.notInUse_leftDir:
            return False, Relationship.Direction.left
        elif enum == cls.InUseAndDir.notInUse_rightDir:
            return False, Relationship.Direction.right
        elif enum == cls.InUseAndDir.undefined:
            return False, Relationship.Direction.undefined
        else:
            raise TypeError("Enum is not of type InUseAndDir")

    @classmethod
    def enum_from_in_use_dir(cls, in_use, direction):
        """
        Create an enum containing the in use value and direction given

        :param in_use: Whether the relationship is being used
        :type in_use: bool
        :param direction: Left or right
        :type direction: Direction
        :return: Enum containing both values
        :rtype: InUseAndDir
        """
        if direction == Relationship.Direction.left:
            if in_use:
                return cls.InUseAndDir.inUse_leftDir
            else:
                return cls.InUseAndDir.notInUse_leftDir
        elif direction == Relationship.Direction.right:
            if in_use:
                return cls.InUseAndDir.inUse_rightDir
            else:
                return cls.InUseAndDir.notInUse_rightDir
        elif direction == Relationship.Direction.undefined:
            return cls.InUseAndDir.undefined
        else:
            raise TypeError("Given direction is not of type Direction")
