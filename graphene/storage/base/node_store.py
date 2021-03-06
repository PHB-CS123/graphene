import struct

from graphene.storage.base.general_store import *
from graphene.storage.base.node import *


class NodeStore(GeneralStore):
    """
    Handles storage of nodes to a file. It stores nodes using the format
    (inUse, nextRelId, nextPropId, nodeType)
    """

    # Format string used to compact these values
    # '=': native byte order representation, standard size, no alignment
    # '?': boolean
    # 'I': unsigned int
    STRUCT_FORMAT_STR = "= ? I I I"
    ''':type: str'''

    # Size of an individual record (bytes)
    RECORD_SIZE = struct.calcsize(STRUCT_FORMAT_STR)
    ''':type: int'''

    # Name of NodeStore File
    FILE_NAME = "graphenestore.nodestore.db"
    ''':type: str'''

    # Type stored by this class
    STORAGE_TYPE = Node

    def __init__(self):
        """
        Creates a NodeStore instance which handles reading/writing to the
        file containing Node values.

        :return: NodeStore instance for handling Node records
        :rtype: NodeStore
        """

        # Initialize using generic base class
        super(NodeStore, self).__init__(self.FILE_NAME, self.RECORD_SIZE)

    def item_from_packed_data(self, index, packed_data):
        """
        Creates a node from the given packed data

        :param index: Index of the node that the packed data belongs to
        :type index: int
        :param packed_data: Packed binary data
        :return: Node from packed data
        :rtype: Node
        """

        # Unpack the data using the Node struct format
        node_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        unpacked_data = node_struct.unpack(packed_data)

        # Get the node components
        in_use = unpacked_data[0]
        rel_id = unpacked_data[1]
        prop_id = unpacked_data[2]
        node_type = unpacked_data[3]

        # Empty data, deleted item
        if in_use is False and rel_id == 0 and prop_id == 0 and node_type == 0:
            return None
        # Create a node record with these components
        else:
            return Node(index, in_use, rel_id, prop_id, node_type)

    def packed_data_from_item(self, item):
        """
        Creates packed data with Node structure to be written to a file

        :param item: Node to convert into packed data
        :type item: Node
        :return: Packed data
        :rtype: bytes
        """

        # Pack the node into a struct with the order (inUse, relId, propId)
        node_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        packed_data = node_struct.pack(item.inUse, item.relId,
                                       item.propId, item.nodeType)

        return packed_data

    def empty_struct_data(self):
        """
        Creates a packed struct of 0s

        :return: Packed class struct of 0s
        :rtype: bytes
        """
        empty_struct = struct.Struct(self.STRUCT_FORMAT_STR)
        packed_data = empty_struct.pack(0, 0, 0, 0)
        return packed_data