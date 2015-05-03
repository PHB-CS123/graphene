from graphene.storage.base.property import *


class Array():
    def __init__(self, index=0, in_use=True,
                 array_type=Property.PropertyType.undefined,
                 previous_block=0, amount=0, next_block=0, items=None):
        """
        Initializes an Array object with the given values

        :param index: Index of start of array
        :type index: int
        :param in_use: Whether the database is using the array
        :type in_use: bool
        :param previous_block: Index of previous block of data
        :type previous_block: int
        :param amount: Number of items stored in this array block
        :type amount: int
        :param next_block: Index of next block of data
        :type next_block: int
        :param items: Items stored with this header
        :type items: list
        :return: Array instance with the specified values
        :rtype: Array
        """
        # Index of the array is not stored in the ArrayStore
        self.index = index
        # Values stored in the ArrayStore
        self.inUse = in_use
        self.type = array_type
        self.previousBlock = previous_block
        self.amount = amount
        self.nextBlock = next_block
        self.items = items

    def __eq__(self, other):
        """
        Overload the == operator
        :param other: Other array
        :type other: Array
        :return: True if equivalent, false otherwise
        :rtype: bool
        """
        if isinstance(other, self.__class__):
            return (self.index == other.index) and \
                   (self.inUse == other.inUse) and \
                   (self.type == other.type) and \
                   (self.previousBlock == other.previousBlock) and \
                   (self.amount == other.amount) and \
                   (self.nextBlock == other.nextBlock) and \
                   (self.items == other.items)
        else:
            return False

    def __ne__(self, other):
        """
        Overload the != operator

        :param other: Other array
        :type other: Array
        :return: True if not equivalent, false otherwise
        :rtype: bool
        """
        return not (self == other)