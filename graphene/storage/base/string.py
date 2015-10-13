class String:
    def __init__(self, index=0, in_use=True, previous_block=0,
                 length=0, next_block=0, string=''):
        """
        Initializes a String with the given values

        :param index: Index of the string
        :type index: int
        :param in_use: Whether the database is using the string
        :type in_use: bool
        :param previous_block: Index of previous block of data
        :type previous_block: int
        :param length: Number of blocks for the whole string
        :type length: int
        :param next_block: Index of next block of data
        :type next_block: int
        :param string: String part stored with this header
        :type string: str
        :return: String instance with the specified values
        :rtype: String
        """

        # Index of the string is not stored in the StringStore
        self.index = index
        # Values stored in the StringStore
        self.inUse = in_use
        self.previousBlock = previous_block
        self.length = length
        self.nextBlock = next_block
        self.string = string

    def __eq__(self, other):
        """
        Overload the == operator

        :param other: Other string
        :type other: String
        :return: True if equivalent, false otherwise
        :rtype: bool
        """

        if isinstance(other, self.__class__):
            return (self.index == other.index) and \
                   (self.inUse == other.inUse) and \
                   (self.previousBlock == other.previousBlock) and \
                   (self.length == other.length) and \
                   (self.nextBlock == other.nextBlock) and \
                   (self.string == other.string)
        else:
            return False

    def __ne__(self, other):
        """
        Overload the != operator

        :param other: Other string
        :type other: String
        :return: True if not equivalent, false otherwise
        :rtype: bool
        """
        return not (self == other)

    def __repr__(self):
        data = ["String", "index = %d" % self.index]
        if self.inUse:
            data.append("in use")
        if self.previousBlock != 0:
            data.append("prev = %d" % self.previousBlock)
        if self.nextBlock != 0:
            data.append("next = %d" % self.nextBlock)
        if self.length != 0:
            data.append("length = %d" % self.length)
        data.append("string = '%s'" % self.string)
        return "[%s]" % " | ".join(data)
