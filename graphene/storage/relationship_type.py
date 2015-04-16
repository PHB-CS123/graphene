class RelationshipType:
    """
    Stores
    """

    def __init__(self, index=0, in_use=True, type_block_id=0):
        """
        Initialize a RelationshipType record.

        :param index: Index of relationship type
        :param in_use: Whether relationship type is in use
        :param typeBlockId: ID of the block that stores string name of our type
        :return: relationship type instance
        """
        # Index is only stored in memory.
        self.index = index

        self.in_use = in_use
        # Create dynamic store (private) for storing relationship type name.
        self.type_block_id = type_block_id
