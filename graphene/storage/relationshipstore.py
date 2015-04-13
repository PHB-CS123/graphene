import struct

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
        undefined = 0
        inUse_rightDir = 0b0001
        inUse_leftDir = 0b0010
        notInUse_rightDir = 0b0100
        notInUse_leftDir = 0b1000

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # 'B': unsigned char
    # 'I': unsigned int
    STRUCT_FORMAT_STR = "= B I I I I I I I I"
    ''':type: str'''

    # Size of an individual record (bytes)
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT_STR)
    ''':type: int'''

    # Name of RelationshipStore File
    FILE_NAME = "graphenestore.relationshipstore.db"
    ''':type: str'''

    def __init__(self):
        """
        Creates a RelationshipStore instance which handles reading/writing to
        the file containing relationship values

        :return: RelationshipStore instance for handling relationship records
        :rtype: RelationshipStore
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
            raise IOError("ERROR: unable to open RelationshipStore file: " +
                          file_path)

    def pad_file_header(self):
        """
        Called when the RelationshipStore file is first created, pads the
        RelationshipStore file with 33 bytes of 0s

        :return: Nothing
        :rtype: None
        """
        # Create a packed struct of 0s
        packed_data = self.empty_struct_data()
        # File pointer should be at 0, no need to seek
        self.storeFile.write(packed_data)

    def relationship_at_index(self, index):
        """
        Finds the relationship with the given relationship index

        :param index: Index of relationship
        :type index: int
        :return: Relationship with given index
        :rtype: Relationship
        """
        if index == 0:
            raise ValueError("Relationship cannot be read from index 0")

        file_offset = index * self.RECORD_SIZE

        # Seek to the calculated offset
        self.storeFile.seek(file_offset)

        # Get the packed data from the file
        packed_data = self.storeFile.read(self.RECORD_SIZE)

        return self.relationship_from_packed_data(index, packed_data)

    def write_relationship(self, relationship):
        """
        Writes the given relationship to the RelationshipStore

        :param relationship: Relationship to write
        :type relationship: Relationship
        :return: Nothing
        :rtype: None
        """
        # Pack the relationship data
        packed_data = self.packed_data_from_relation(relationship)
        # Write the packed data to the relationship index
        self.write_to_index_packed_data(relationship.index, packed_data)

    def delete_relationship(self, relationship):
        """
        Deletes the given relationship from the RelationshipStore

        :param relationship: Relationship to delete
        :type relationship: Relationship
        :return: Nothing
        :rtype: None
        """
        self.delete_relationship_at_index(relationship.index)

    def delete_relationship_at_index(self, index):
        """
        Deletes the relationship at the given index from the RelationshipStore

        :param index: Index of the relationship
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
            raise ValueError("Relationship cannot be written to index 0")

        file_offset = index * self.RECORD_SIZE

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
        :return: Relationship from packed data
        :rtype: Relationship
        """

        # Unpack the data using the relationship struct format
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
        Creates packed data with Relationship structure to be written to a file

        :param relationship: Relationship to convert into packed data
        :type relationship: Relationship
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
