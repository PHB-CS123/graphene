class GeneralType:
    def __init__(self, index=0, in_use=True, name_id=0, first_type=0):
        """
        General type for Nodes and Relationships

        :param index: Index where the type is stored
        :type index: int
        :param in_use: Whether the type is in use
        :type in_use: bool
        :param name_id: Index where the name is stored
        :type name_id: int
        :param first_type: Index of the first type of this type, i.e.
                           for Person(name: str, age:int), this would
                           point to name
        :type first_type: int
        :return: General type instance for Relationship or Node types
        :rtype: GeneralType
        """
        # Index of the type is not stored in the GeneralTypeStore file
        self.index = index
        # Values stored in the GeneralTypeStore file
        self.inUse = in_use
        self.nameId = name_id
        self.firstType = first_type

    def __eq__(self, other):
        """
        Overload the == operator

        :param other: Other general type
        :type other: GeneralType
        :return: True if equivalent, false otherwise
        :rtype: bool
        """
        if isinstance(other, self.__class__):
            return (self.index == other.index) and \
                   (self.inUse == other.inUse) and \
                   (self.nameId == other.nameId) and \
                   (self.firstType == other.firstType)
        else:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __repr__(self):
        data = ["Type", "index = %d" % self.index]
        if self.inUse:
            data.append("in use")
        if self.nameId is not 0:
            data.append("name_id = %s" % self.nameId)
        if self.firstType != 0:
            data.append("first_type = %d" % self.firstType)
        return "[%s]" % " | ".join(data)
