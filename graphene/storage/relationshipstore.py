import struct
import os.path
from enum import Enum

from graphene.storage.graphenestore import *
from graphene.storage.relationship import *

class RelationshipStore:
    """
    Handles storage of relationships to a file. It stores relationships using
    the format:
    (inUse_direction, firstNode, secondNode, relType, firstPrevRelId,
     firstNextRelId, secondPrevRelId, secondNextRelId, nextPropId)
    """

    class InUseAndDir(Enum):
        in_use_right_dir = 0b0001
        in_use_left_dir = 0b0010
        not_in_use_right_dir = 0b0100
        not_in_use_left_dir = 0b1000

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # 'B': unsigned char
    # 'I': unsigned int
    STRUCT_FORMAT_STR = "= B I I I I I I I I"
    ''':type: str'''

    # Size of an individual record (bytes)
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT_STR)
    ''':type: int'''

    # Name of NodeStore File
    FILE_NAME = "graphenestore.relationshipstore.db"
    ''':type: str'''

    def __init__(self):
        """
        Creates a RelationshipStore instance which handles reading/writing to
        the file containing Relationship values
        :return: RelationshipStore instance for handling Relationship records
        :rtype: RelationshipStore
        """
        try:
            graphenestore = GrapheneStore()
            # Get the path of the file
            file_path = graphenestore.datafilesDir + self.FILE_NAME
            # If the file exists, simply open it
            if os.path.isfile(file_path):
                self.storeFile = open(file_path, "r+b")
            else:
                # Create the file
                open(file_path, "w+").close()
                # Open it so that it can be read/written
                self.storeFile = open(file_path, "r+b")
                # Pad its first 9 bytes with 0s
                self.padFileHeader()
        except IOError:
            print("ERROR: unable to open relationship store file: ", file_path)
            raise IOError

    def padFileHeader(self):
        """
        Called when the RelationshipStore file is first created, pads the
        RelationshipStore file with 9 bytes of 0s
        :return: Nothing
        :rtype: None
        """
        # Create a packed struct of 0s
        packed_data = self.empty_struct_data()
        # File pointer should be at 0, no need to seek
        self.storeFile.write(packed_data)

    def relationship_at_index(self, index):
        """
        Finds the Relationship with the given Relationship index
        :param index: Index of relationship
        :type index: int
        :return: Relationship with given index
        :rtype: Relationship
        """
        file_offset = index * self.RECORD_SIZE
        # Seek to the calculated offset
        self.storeFile.seek(file_offset)

        # Get the packed data from the file
        packed_data = self.storeFile.read(self.RECORD_SIZE)

        return self.relationship_from_packed_data(index, packed_data)

    def write_relationship(self, relationship):
        """
        Writes the given Relationship to the RelationshipStore file
        :param relationship: Relationship to write to offset
        :type relationship: Relationship
        :return: Nothing
        :rtype: None
        """

        file_offset = relationship.index * self.RECORD_SIZE

        if file_offset == 0:
            raise ValueError("Relationship cannot be written to offset 0")

        # Pack the relationship data
        packed_data = self.packed_data_from_relation(relationship)

        # Seek to the calculated offset and write the data
        self.storeFile.seek(file_offset)
        self.storeFile.write(packed_data)


    @classmethod
    def relationship_from_packed_data(cls, index, packed_data):
        """
        Creates a relationship from the given packed data
        :param index: Index of the relationship the packed data belongs to
        :type index: int
        :param packed_data: Packed binary data
        :return: Node from packed data
        :rtype: Node
        """

        # Unpack the data using the Relationship struct format
        relationship_struct = struct.Struct(cls.STRUCT_FORMAT_STR)
        unpacked_data = relationship_struct.unpack(packed_data)

        # Get the relationship components

        # Get in use and direction from byte, make enum and extract values
        in_use_dir = unpacked_data[0]
        enum = cls.InUseAndDir(in_use_dir)
        (in_use, direction) = cls.in_use_dir_from_enum(enum)

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

    @classmethod
    def packed_data_from_relation(cls, relationship):
        """
        Creates packed data with Relation structure to be written to a file
        :param relationship: Relation to convert into packed data
        :type relationship: Relation
        :return: Packed data
        """

        # Pack the relationship into a struct with the order
        # (inUse_direction, firstNode, secondNode, relType, firstPrevRelId,
        #  firstNextRelId, secondPrevRelId, secondNextRelId, nextPropId)
        relationship_struct = struct.Struct(cls.STRUCT_FORMAT_STR)

        # Create enum to combine the in use and direction values
        enum = cls.enum_from_in_use_dir(relationship.inUse,
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

    @classmethod
    def empty_struct_data(cls):
        """
        Creates a packed struct of 0s
        :return: Packed class struct of 0s
        """
        empty_struct = struct.Struct(cls.STRUCT_FORMAT_STR)
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
        if enum == cls.InUseAndDir.in_use_left_dir:
            return True, Direction.left
        elif enum == cls.InUseAndDir.in_use_right_dir:
            return True, Direction.right
        elif enum == cls.InUseAndDir.not_in_use_left_dir:
            return False, Direction.left
        elif enum == cls.InUseAndDir.not_in_use_right_dir:
            return False, Direction.right
        elif isinstance(enum, cls.InUseAndDir):
            raise ValueError("Invalid InUseAndDir value")
        else:
            raise TypeError("Enum is not of type InUseAndDir")

    @classmethod
    def enum_from_in_use_dir(cls, in_use, direction):
        """
        Create an enum containing the in use value and direction given
        :param in_use: Whether the node is being used
        :type in_use: bool
        :param direction: Left or right
        :type direction: Direction
        :return: Enum containing both values
        :rtype: InUseAndDir
        """
        if direction == Direction.left:
            if in_use:
                return cls.InUseAndDir.in_use_left_dir
            else:
                return cls.InUseAndDir.not_in_use_left_dir
        elif direction == Direction.right:
            if in_use:
                return cls.InUseAndDir.in_use_right_dir
            else:
                return cls.InUseAndDir.not_in_use_right_dir
        elif isinstance(direction, Direction):
            raise ValueError("Invalid Direction value")
        else:
            raise TypeError("Given direction is not fo type Direction")
