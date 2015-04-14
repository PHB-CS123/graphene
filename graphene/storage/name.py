
class Name:
    def __init__(self, index=0, in_use=True, previous_block=0,
                 length=0, next_block=0, name=''):
        """
        Initializes a Name with the given values

        :param index: Index of the name
        :type index: int
        :param in_use: Whether the database is using the name
        :type in_use: bool
        :param previous_block:
        :type previous_block:
        :param length:
        :type length:
        :param next_block:
        :type next_block:
        :param name:
        :type name:
        :return:
        :rtype:
        """

        # Index of the name is not stored in the NameStore
        self.index = index
        # Values stored in the NameStore
        self.inUse = in_use
        self.previousBlock = previous_block
        self.length = length
        self.nextBlock = next_block
        self.name = name

    def __eq__(self, other):
        """
        Overload the == operator

        :param other: Other name
        :type other: Name
        :return: True if equivalent, false otherwise
        :rtype: bool
        """

        if isinstance(other, self.__class__):
            return (self.index == other.index) and \
                   (self.inUse == other.inUse) and \
                   (self.previousBlock == other.previousBlock) and \
                   (self.length == other.length) and \
                   (self.nextBlock == other.nextBlock)
        else:
            return False