class RelationshipType:
    """
    Stores components of a relationship type:
        inUse: Whether relationship type is in use
        type_block_id: ID of the block that stores string name of our type
    Along with the index where the relationship type is stored
    """

    def __init__(self, index=0, in_use=True, type_block_id=0):
        """
        Initialize a RelationshipType record.

        :param index: Index of relationship type
        :type index: int
        :param in_use: Whether relationship type is in use
        :type in_use: bool
        :param type_block_id: ID of the block that stores string
                              name of our type
        :type type_block_id: int
        :return: relationship type instance
        :rtype: RelationshipType
        """
        # Index is only stored in memory.
        self.index = index
        # Values stored in the RelationshipTypeStore file
        self.inUse = in_use
        self.typeBlockId = type_block_id

    def __eq__(self, other):
        """
        Overload the == operator

        :param other: Other relationship type
        :type other: RelationshipType
        :return: True if equivalent, false otherwise
        :rtype: bool
        """

        if isinstance(other, self.__class__):
            return (self.index == other.index) and \
                   (self.inUse == other.inUse) and \
                   (self.typeBlockId == other.typeBlockId)
        else:
            return False

    def __ne__(self, other):
        """
        Overload the != operator

        :param other: Other relationship type
        :type other: RelationshipType
        :return: True if not equivalent, false otherwise
        :rtype: bool
        """
        return not (self == other)