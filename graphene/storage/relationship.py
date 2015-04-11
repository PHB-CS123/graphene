from enum import Enum

class Direction(Enum):
    left = 0
    right = 1

class Relationship:

    def __init__(self, index = 0, in_use=False, direction=Direction.right,
                 first_node_id=0, second_node_id=0, rel_type=0,
                 first_prev_rel_id=0, first_next_rel_id=0,
                 second_prev_rel_id=0, second_next_rel_id=0,
                 prop_id=0):
        """
        Initializes a relationship with the given values
        :param index: Index of the relationship to initialize
        :type index: int
        :param in_use:  Whether the database is using the relationship
        :type in_use: int
        :param direction: Direction of the relationship (right, left)
        :type direction: Direction
        :param first_node_id: ID of the first node in the relation
        :type first_node_id: int
        :param second_node_id: ID of the second node in the relationship
        :type second_node_id: int
        :param rel_type: Id of the relationship type
        :type rel_type: int
        :param first_prev_rel_id: ID of the prev relation of the first node
        :type first_prev_rel_id: int
        :param first_next_rel_id: ID of the next relation of the first node
        :type first_next_rel_id: int
        :param second_prev_rel_id: ID of the prev relation of the second node
        :type second_prev_rel_id: int
        :param second_next_rel_id: ID of the next relation of the second node
        :type second_next_rel_id: int
        :param prop_id: ID of the first property the relationship has
        :type prop_id: int
        :return: Relationship instance with the specified values
        :rtype: Relationship
        """
        # Index of the relationship is not stored in the RelationshipStore file
        self.index = index
        # Values stored in the relationship file
        self.inUse = in_use
        self.direction = direction
        self.firstNodeId = first_node_id
        self.secondNodeId = second_node_id
        self.relType = rel_type
        self.firstPrevRelId = first_prev_rel_id
        self.firstNextRelId = first_next_rel_id
        self.secondPrevRelId = second_prev_rel_id
        self.secondNextRelId = second_next_rel_id
        self.propId = prop_id

    def __eq__(self, other):
        """
        Overload the == operator
        :param other: Other relationship
        :type other: Relationship
        :return: True if equivalent, false otherwise
        :rtype: bool
        """
        if isinstance(other, self.__class__):
            return (self.index == other.index) and \
                   (self.inUse == other.inUse) and \
                   (self.direction == other.direction) and \
                   (self.firstNodeId == other.firstNodeId) and \
                   (self.secondNodeId == other.secondNodeId) and \
                   (self.relType == other.relType) and \
                   (self.firstPrevRelId == other.firstPrevRelId) and \
                   (self.firstNextRelId == other.firstNextRelId) and \
                   (self.secondPrevRelId == other.secondPrevRelId) and\
                   (self.secondNextRelId == other.secondNextRelId) and \
                   (self.propId == other.propId)
        else:
            return False