from graphene.storage.graphene_store import *
from graphene.storage.relationship_type import *

import struct


class RelationshipTypeStore:
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
    STRUCT_FORMAT_STR = "= ? i"
    ''':type: str'''

    # Size of an individual record (bytes)
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT_STR)
    ''':type: int'''

    # Name of RelationshipTypeStore File
    FILE_NAME = "graphenestore.relationshiptypestore.db"
    ''':type: str'''

    def __init__(self):
        """
        Creates a RelationshipTypeStore instance.

        :return: RelationshipStore instance for handling relationship records
        :rtype: RelationshipStore
        """
        # Create a dynamic store for ourselves.
        self.dynamic_store = None

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
            raise IOError("ERROR: unable to open RelationshipTypeStore file: " +
                          file_path)

    def pad_file_header(self):
        """
        Pads the RelationshipTypeStore file with zeroes.

        :return: Nothing
        :rtype: None
        """
        # Create a packed struct of 0s
        packed_data = self.empty_struct_data()
        # File pointer should be at 0, no need to seek
        self.storeFile.write(packed_data)

    def relationship_type_at_index(self, index):
        """
        Finds the relationship type name with the index.

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
        type_block_id = self.storeFile.read(self.RECORD_SIZE)

        # TODO: Read type_block_id from DynamicStore
        return self.dynamic_store.read(type_block_id)

    def write_relationship_type(self, index, rel_type):
        """
        Writes the given relationship type to the RelationshipTypeStore file.

        :param rel_type: String relationship type to write.
        :type rel_type: str
        :param index: Index in file to write to.
        :type index: int
        :return: Nothing
        :rtype: None
        """
        if index == 0:
            raise IOError("Cannot write relationship type to index 0!")

        # TODO: Write the string to the dynamic store and get a pointer.
        type_block_id = self.dynamic_store.write(rel_type)

        rel_type_obj = RelationshipType(index, False, type_block_id)

        # Pack the relationship data
        packed_data = self.packed_data_from_relationship_type(rel_type_obj)
        # Write the packed data to the relationship index
        self.write_to_index_packed_data(index, packed_data)

    def delete_relationship_type(self, rel_type):
        """
        Deletes the given relationship type from the RelationshipStoreType

        :param rel_type: Relationship type to delete
        :type rel_type: RelationshipType
        :return: Nothing
        :rtype: None
        """
        self.delete_relationship_at_index(rel_type.index)

    def delete_relationship_at_index(self, index):
        """
        Deletes the relationship type at the given index from the
        RelationshipTypeStore.

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
            raise ValueError("Relationship type cannot be written to index 0")

        file_offset = index * self.RECORD_SIZE

        # Seek to the calculated offset and write the data
        self.storeFile.seek(file_offset)
        self.storeFile.write(packed_data)

    @classmethod
    def empty_struct_data(cls):
        """
        Creates a packed struct of 0s

        :return: Packed class struct of 0s
        """
        empty_struct = struct.Struct(cls.STRUCT_FORMAT_STR)
        packed_data = empty_struct.pack(0, 0)
        return packed_data

    @classmethod
    def packed_data_from_relationship_type(cls, relationship_type):
        """
        Create packed data with RelationshipType structure to be written.

        :param relationship_type: RelationshipType object to convert.
        :type relationship_type: RelationshipType
        :return: Packed data string.
        """
        relationship_type_struct = struct.Struct(cls.STRUCT_FORMAT_STR)

        packed_data = relationship_type_struct.pack(
            relationship_type.in_use, relationship_type.type_block_id)

        return packed_data
