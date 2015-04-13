import struct

from graphene.storage.graphenestore import *
from graphene.storage.node import *


class NodeStore:
    """
    Handles storage of nodes to a file. It stores nodes using the format
    (inUse, nextRelId, nextPropId)
    """

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # '?': boolean
    # 'I': unsigned int
    STRUCT_FORMAT_STR = "= ? I I"
    ''':type: str'''

    # Size of an individual record (bytes)
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT_STR)
    ''':type: int'''

    # Name of NodeStore File
    FILE_NAME = "graphenestore.nodestore.db"
    ''':type: str'''

    def __init__(self):
        """
        Creates a NodeStore instance which handles reading/writing to the
        file containing Node values.

        :return: NodeStore instance for handling Node records
        :rtype NodeStore
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
            raise IOError("ERROR: unable to open NodeStore file: " + file_path)

    def pad_file_header(self):
        """
        Called when the NodeStore file is first created, pads the NodeStore
        file with 9 bytes of 0s

        :return: Nothing
        :rtype: None
        """
        # Create a packed struct of 0s
        packed_data = self.empty_struct_data()
        # File pointer should be at 0, no need to seek
        self.storeFile.write(packed_data)

    def node_at_index(self, index):
        """
        Finds the Node with the given Node index

        :param index: Index of node
        :type index: int
        :return: Node with given index
        :rtype: Node
        """
        if index == 0:
            raise ValueError("Node cannot be read from index 0")

        file_offset = index * self.RECORD_SIZE

        # Seek to the calculated offset
        self.storeFile.seek(file_offset)

        # Get the packed data from the file
        packed_data = self.storeFile.read(self.RECORD_SIZE)

        return self.node_from_packed_data(index, packed_data)

    def write_node(self, node):
        """
        Writes the given Node to the NodeStore file

        :param node: Node to write
        :type: node: Node
        :return: Nothing
        :rtype: None
        """
        # Pack the node data, then write it to the node index
        packed_data = self.packed_data_from_node(node)
        # Write the packed data to the node index
        self.write_to_index_packed_data(node.index, packed_data)

    def delete_node(self, node):
        """
        Deletes the given node from the NodeStore

        :param node: Node to delete
        :type node: Node
        :return: Nothing
        :rtype: None
        """
        self.delete_node_at_index(node.index)

    def delete_node_at_index(self, index):
        """
        Deletes the node at the given index from the NodeStore

        :param index: Index of the node
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
            raise ValueError("Node cannot be written to index 0")

        file_offset = index * self.RECORD_SIZE

        # Seek to the calculated offset and write the data
        self.storeFile.seek(file_offset)
        self.storeFile.write(packed_data)


    @classmethod
    def node_from_packed_data(cls, index, packed_data):
        """
        Creates a node from the given packed data

        :param index: Index of the node that the packed data belongs to
        :type index: int
        :param packed_data: Packed binary data
        :return: Node from packed data
        :rtype: Node
        """

        # Unpack the data using the Node struct format
        node_struct = struct.Struct(cls.STRUCT_FORMAT_STR)
        unpacked_data = node_struct.unpack(packed_data)

        # Get the node components
        in_use = unpacked_data[0]
        rel_id = unpacked_data[1]
        prop_id = unpacked_data[2]

        # Create a node record with these components
        return Node(index, in_use, rel_id, prop_id)

    @classmethod
    def packed_data_from_node(cls, node):
        """
        Creates packed data with Node structure to be written to a file

        :param node: Node to convert into packed data
        :type node: Node
        :return: Packed data
        """

        # Pack the node into a struct with the order (inUse, relId, propId)
        node_struct = struct.Struct(cls.STRUCT_FORMAT_STR)
        packed_data = node_struct.pack(node.inUse, node.relId, node.propId)

        return packed_data

    @classmethod
    def empty_struct_data(cls):
        """
        Creates a packed struct of 0s

        :return: Packed class struct of 0s
        """
        empty_struct = struct.Struct(cls.STRUCT_FORMAT_STR)
        packed_data = empty_struct.pack(0, 0, 0)
        return packed_data

    def __del__(self):
        """
        Closes the NodeStore file

        :return: Nothing
        :rtype: None
        """
        self.storeFile.close()

