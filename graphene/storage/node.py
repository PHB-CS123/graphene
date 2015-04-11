class Node:
    """
    Stores components of a node:
        inUse: Whether the database is using the node
        relId: ID of the first relation the node has
        propId: ID of the first property the node has
    Along with the index where the node is stored
    """
    def __init__(self, index=0, in_use=False, rel_id=0, prop_id=0):
        """
        Initializes a Node with the given values
        :param index: Index of the node to initialize
        :type index: int
        :param in_use: Whether the database is using the node
        :type in_use: int
        :param rel_id: ID of the first relation the node has
        :type rel_id: int
        :param prop_id: ID of the first property the node has
        :type prop_id: int
        :return: Node instance with the specified values
        :rtype: Node
        """
        # Index of the node is not stored in the NodeStore file
        self.index = index
        # Values stored in the NodeStore file
        self.inUse = in_use
        self.relId = rel_id
        self.propId = prop_id

    def __eq__(self, other):
        """
        Overload the == operator
        :param other: Other node
        :type other: Node
        :return: True if equivalent, false otherwise
        :rtype: bool
        """

        if isinstance(other, self.__class__):
            return (self.index == other.index) and \
                   (self.inUse == other.inUse) and \
                   (self.relId == other.relId) and \
                   (self.propId == other.propId)
        else:
            return False