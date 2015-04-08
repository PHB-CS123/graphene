import struct

from Node import *


class NodeStore:
    """
    Handles storage of nodes to a file. It stores nodes using the format
    (inUse, nextRelId, nextPropId)
    """
    # Size of parts of NodeStore records (bytes)

    # Whether the node is in use
    IN_USE_SIZE = 1
    ''':type: int'''
    # First relation of this node
    NEXT_REL_ID_SIZE = 4
    ''':type: int'''
    # First property of this node
    NEXT_PROP_ID_SIZE = 4
    ''':type: int'''

    # Format string used to compact these values
    # '<': little endian representation
    # '?': boolean
    # 'I': unsigned int
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
        :return: NodeStore instance for handling Node record types
        :rtype NodeStore
        """

        try:
            self.storeFile = open(NodeStore.FILE_NAME, "ab+")
        except IOError:
            print("ERROR: unable to open node store file: ", NodeStore.FILE_NAME)

    def node_with_index(self, index):
        """
        Finds the Node with the given Node index
        :param index: Index of node
        :type index: int
        :return: Node with given index
        :rtype: None
        """

        file_offset = index * NodeStore.RECORD_SIZE
        return self.node_at_offset(file_offset)


    def node_at_offset(self, file_offset):
        """
        Gets the node at the given file offset (bytes)
        :param file_offset: Offset of the node in the file (in bytes)
        :type file_offset: int
        :return: Node stored at the given offset
        :rtype: Node
        """
        # Seek to the given offset
        self.storeFile.seek(file_offset)

        packed_data = self.storeFile.read(NodeStore.RECORD_SIZE)

        return self.node_from_packed_data(packed_data)

    def write_node_to_offset(self, file_offset, node):
        """
        Writes the data to the NodeStore file at the given offset
        :param file_offset: Offset in bytes
        :type file_offset: int
        :param node: Node to write to offset
        :type: node: Node
        :return: Nothing
        :rtype: None
        """
        # Pack the node data, then write it to the specified offset
        packed_data = self.packed_data_from_node(node)

        # Seek to the given offset and write the data
        self.storeFile.seek(file_offset)
        self.storeFile.write(packed_data)


    @classmethod
    def node_from_packed_data(cls, packed_data):
        """
        Creates a node from the given packed data
        :param packed_data: Packed binary data
        :return: Node from packed data
        :rtype: Node
        """

        # Unpack the data using the Node struct format
        node_struct = struct.Struct(NodeStore.STRUCT_FORMAT_STR)
        unpacked_data = node_struct.unpack(packed_data)

        # Get the node components
        in_use = unpacked_data[0]
        node_id = unpacked_data[1]
        rel_id = unpacked_data[2]

        # Create a node record with these components
        return Node(in_use, node_id, rel_id)

    @classmethod
    def packed_data_from_node(cls, node):
        """
        Creates packed data with Node structure to be written to a file
        :param node: Node to convert into packed data
        :type node: Node
        :return: Packed data
        """

        # Pack the node into a struct with the order (inUse, nodeId, relId)
        node_struct = struct.Struct(NodeStore.STRUCT_FORMAT_STR)
        packed_data = node_struct.pack(node.inUse, node.nodeId, node.relId)

        return packed_data

    def __del__(self):
        """
        Closes the NodeStore file
        :return: Nothing
        :rtype: None
        """
        self.storeFile.close()

