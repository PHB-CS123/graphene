class Node:
    """
    Stores components of a node:
        inUse: Whether the database is using the node
        relId: ID of the first relation the node has
        propId: ID of the first property the node has
    """
    def __init__(self, in_use=0, rel_id=0, prop_id=0):
        """
        Initializes a Node with the given values
        :param in_use: Whether the database is using the node
        :type in_use: int
        :param rel_id: ID of the first relation the node has
        :type rel_id: int
        :param prop_id: ID of the first property the node has
        :type prop_id: int
        :return: Node instance with the specified values
        :rtype: Node
        """
        self.inUse = in_use
        self.relId = rel_id
        self.propId = prop_id