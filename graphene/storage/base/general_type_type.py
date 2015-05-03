from graphene.storage.base.property import *


class GeneralTypeType:
    """
    Stores type components of a Node or Relationship type:
        inUse: Whether the db is using the type of the Node/Relationship type
        typeName: ID used to locate the property name in the name store
        propertyType: Type of property primitive
        nextType: Next type for this Node/Relationship type
    Along with the index where the type of the type is stored
    """
    def __init__(self, index=0, in_use=True, type_name=0,
                 property_type=Property.PropertyType.undefined,
                 next_type=0):

        # Index of the node is not stored in the NodeStore file
        self.index = index
        # Values stored in the NodeStore file
        self.inUse = in_use
        self.typeName = type_name
        self.propertyType = property_type
        self.nextType = next_type

    def __eq__(self, other):
        """
        Overload the == operator

        :param other: Other type of type
        :type other: GeneralTypeType
        :return: True if equivalent, false otherwise
        :rtype: bool
        """

        if isinstance(other, self.__class__):
            return (self.index == other.index) and \
                   (self.inUse == other.inUse) and \
                   (self.typeName == other.typeName) and \
                   (self.propertyType == other.propertyType) and \
                   (self.nextType == other.nextType)
        else:
            return False

    def __ne__(self, other):
        """
        Overload the != operator

        :param other: Other general type type
        :type other: GeneralTypeType
        :return: True if not equivalent, false otherwise
        :rtype: bool
        """
        return not (self == other)

    def __repr__(self):
        data = ["TypeType", "index = %d" % self.index]
        if self.inUse:
            data.append("in use")
        if self.typeName is not 0:
            data.append("name_id = %s" % self.typeName)
        if self.propertyType is not Property.PropertyType.undefined:
            data.append("type = %s" % self.propertyType)
        if self.nextType != 0:
            data.append("next = %d" % self.nextType)
        return "[%s]" % " | ".join(data)
