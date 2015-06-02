from graphene.storage.base.property import *


class Array:
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
        :param amount: Number of blocks for the whole array
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

    def almost_equal(self, other, precision):
        """
        Check that the items in the two arrays are equal within the
        given number of decimal places

        :param other: Other array
        :type other: Array
        :param precision: Decimal places of precision
        :type precision: int
        :return: True if almost equal, false otherwise
        :rtype: bool
        """
        if isinstance(other, self.__class__):
            # Check that all elements in both arrays are almost
            # equal within given precision
            almost_equal = all(map(lambda x, y:
                                   self.almost_equal_values(x, y, precision),
                                   self.items, other.items))
            return (self.index == other.index) and \
                   (self.inUse == other.inUse) and \
                   (self.type == other.type) and \
                   (self.previousBlock == other.previousBlock) and \
                   (self.amount == other.amount) and \
                   (self.nextBlock == other.nextBlock) and almost_equal
        else:
            return False

    def is_string_array(self):
        """
        Returns whether this is a string array

        :return: True if string array, False otherwise
        :rtype: bool
        """
        return self.type == Property.PropertyType.stringArray

    @staticmethod
    def almost_equal_values(x, y, precision):
        """
        Check that the given items are equal within the given
        number of decimal places (precision

        :param x: first value
        :type x: float
        :param y: second value
        :type y: float
        :param precision: Decimal places of precision
        :type precision: int
        :return: True if almost equal, false otherwise
        :rtype: bool
        """
        return round(x - y, precision) == 0