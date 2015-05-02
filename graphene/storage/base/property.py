from enum import Enum


class Property:
    class PropertyType(Enum):
        # Undefined type
        undefined = 0
        # Primitive types
        int = 1
        long = 2
        bool = 3
        short = 4
        char = 5
        float = 6
        double = 7
        # String type (dynamic)
        string = 8
        # Array types (dynamic)
        intArray = 9
        longArray = 10
        boolArray = 11
        shortArray = 12
        charArray = 13
        floatArray = 14
        doubleArray = 15
        stringArray = 16

    def __init__(self, index=0, in_use=True, prop_type=PropertyType.undefined,
                 name_id=0, prev_prop_id=0, next_prop_id=0, prop_block_id=0):
        """
        Initializes a property with the given values

        :param index: Index of the property to initialize
        :type index: int
        :param in_use: Whether the property is in use
        :type in_use: bool
        :param prop_type: Type of property (int, long, string, etc.)
        :type prop_type: PropertyType
        :param name_id: Pointer to the record holding the property name
        :type name_id: int
        :param prev_prop_id: ID of the prev property owned by node or relation
        :type prev_prop_id: int
        :param next_prop_id: ID of the next property owned by node or relation
        :type next_prop_id: int
        :param prop_block_id: ID to a dynamic store (string or array) or the
                              value if the property is a primitive (int, long,
                              float, etc.)
        :return: Property instance with the specified values
        :rtype: Property
        """
        # Index of the property is not stored in the PropertyStore file
        self.index = index
        # Values stored in the PropertyStore file
        self.inUse = in_use
        self.type = prop_type
        self.nameId = name_id
        self.prevPropId = prev_prop_id
        self.nextPropId = next_prop_id
        self.propBlockId = prop_block_id

    def __eq__(self, other):
        """
        Overload the == operator

        :param other: Other property
        :type other: Property
        :return: True if equivalent, false otherwise
        :rtype: bool
        """
        if isinstance(other, self.__class__):
            return (self.index == other.index) and \
                   (self.inUse == other.inUse) and \
                   (self.type == other.type) and \
                   (self.nameId == other.nameId) and \
                   (self.prevPropId == other.prevPropId) and\
                   (self.nextPropId == other.nextPropId) and \
                   (self.propBlockId == other.propBlockId)
        else:
            return False

    def __ne__(self, other):
        """
        Overload the != operator

        :param other: Other property
        :type other: Property
        :return: True if not equivalent, false otherwise
        :rtype: bool
        """
        return not (self == other)

    def __str__(self):
        """
        String representation of this property.

        :return: Human-readable representation of this property.
        """
        args = (self.index, self.type, self.nameId, self.prevPropId,
                self.nextPropId, self.propBlockId)
        return "Property: %d. Type: %s, nameID: %s, prevPropertyID: %s, " \
               "nextPropertyID: %s, propBlockID: %s" % args
