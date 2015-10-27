from enum import Enum
from collections import OrderedDict

from graphene.storage.base.array import Array
from graphene.storage.base.general_type import GeneralType
from graphene.storage.base.general_type_type import GeneralTypeType
from graphene.storage.base.string import String
from graphene.storage.base.node import Node
from graphene.storage.base.property import Property
from graphene.storage.base.relationship import Relationship

# ----------------------------------- Types ---------------------------------- #

kArrayType = Array.__name__
kGeneralType = GeneralType.__name__
kGeneralTypeType = GeneralTypeType.__name__
kStringType = String.__name__
kNode = Node.__name__
kProperty = Property.__name__
kRelationship = Relationship.__name__

kPayload = (kStringType, kArrayType)


class HeaderType(Enum):
    """ Base header types"""
    bool = 1
    int = 2
    char = 3
    data = 4

# --------------------------------- Constants -------------------------------- #

kPropertyTypeOffset = 1
kPropertyPayloadOffset = 17

# ----------------------------- Offset Descriptor ---------------------------- #

ArrayOffsetDescriptor = {
    0: ("inUse", HeaderType.bool),
    1: ("type",  HeaderType.char),
    2: ("previousBlock", HeaderType.int),
    6: ("amount", HeaderType.int),
    10: ("blocks", HeaderType.int),
    14: ("nextBlock", HeaderType.int),
    18: ("data", HeaderType.data),
}

GeneralTypeOffsetDescriptor = {
    0: ("inUse", HeaderType.bool),
    1: ("nameId", HeaderType.int),
    5: ("firstType", HeaderType.int),
}

GeneralTypeTypeOffsetDescriptor = {
    0: ("inUse", HeaderType.bool),
    1: ("typeName", HeaderType.int),
    5: ("propertyType", HeaderType.int),
    9: ("nextType", HeaderType.int),
}

StringOffsetDescriptor = {
    0: ("inUse", HeaderType.bool),
    1: ("previousBlock", HeaderType.int),
    5: ("length", HeaderType.int),
    9: ("nextBlock", HeaderType.int),
    13: ("data", HeaderType.data),
}

NodeOffsetDescriptor = {
    0: ("inUse", HeaderType.bool),
    1: ("nextRelId", HeaderType.int),
    5: ("nextPropId", HeaderType.int),
    9: ("nodeType", HeaderType.int),
}

PropertyOffsetDescriptor = {
    0: ("inUse", HeaderType.bool),
    1: ("type", HeaderType.int),
    5: ("nameId", HeaderType.int),
    9: ("prevPropId", HeaderType.int),
    13: ("nextPropId", HeaderType.int),
    17: ("propBlockId", HeaderType.data),
}

RelationshipOffsetDescriptor = {
    0: ("inUse_direction", HeaderType.bool),
    1: ("firstNode", HeaderType.int),
    5: ("secondNode", HeaderType.int),
    9: ("generalType", HeaderType.int),
    13: ("firstPrevRelId", HeaderType.int),
    17: ("firstNextRelId", HeaderType.int),
    21: ("secondPrevRelId", HeaderType.int),
    25: ("secondNextRelId", HeaderType.int),
    29: ("nextPropId", HeaderType.int),
}

OffsetDescriptors = {
    kArrayType: ArrayOffsetDescriptor,
    kGeneralType: GeneralTypeOffsetDescriptor,
    kGeneralTypeType: GeneralTypeTypeOffsetDescriptor,
    kStringType: StringOffsetDescriptor,
    kNode: NodeOffsetDescriptor,
    kProperty: PropertyOffsetDescriptor,
    kRelationship: RelationshipOffsetDescriptor,
}


def offset_descriptor_for_class(c):
    """
    Returns the appropriate offset descriptor for the given type class.

    :param c: Class to get an offset descriptor for (must be a base type class)
    :type c: class
    :return: Offset descriptor sorted by dictionary keys
    :rtype: OrderedDict[str, (str, HeaderType)]
    """
    try:
        return OrderedDict(sorted(OffsetDescriptors[c]))
    except KeyError:
        raise TypeError("Unrecognized class type")

# ---------------------------- Offset -> Type Maps --------------------------- #

ArrayOffsetReferenceMap = {
    0: None,                  # inUse (bool, 1 byte)
    1: None,                  # type  (char, 1 byte)
    2: kArrayType,            # previousBlock (int, 4 bytes)
    6: None,                  # amount (int, 4 bytes)
    10: None,                 # blocks (int, 4 bytes)
    14: kArrayType,           # nextBlock (int, 4 bytes)
    18: (None, kStringType)   # Payload (primitives or str references, any size)
}

GeneralTypeOffsetReferenceMap = {
    0: None,              # inUse (bool, 1 byte)
    1: kStringType,       # nameId (int, 4 bytes)
    5: kGeneralTypeType,  # firstType (int, 4 bytes)
}

GeneralTypeTypeOffsetReferenceMap = {
    0: None,              # inUse (bool, 1 byte)
    1: kStringType,       # typeName (int, 4 bytes)
    5: None,              # propertyType (int, 4 bytes)
    9: kGeneralTypeType,  # nextType (int, 4 bytes)
}

StringOffsetReferenceMap = {
    0: None,              # inUse (bool, 1 byte)
    1: kStringType,       # previousBlock (int, 4 bytes)
    5: None,              # length (int, 4 bytes)
    9: kStringType,       # nextBlock (int, 4 bytes)
    13: None              # Payload (part of string, any size)
}

NodeOffsetReferenceMap = {
    0: None,              # inUse (bool, 1 byte)
    1: kRelationship,     # nextRelId (int, 4 bytes)
    5: kProperty,         # nextPropId (int, 4 bytes)
    9: kGeneralType,      # nodeType (int, 4 bytes)
}

PropertyOffsetReferenceMap = {
    0: None,                       # inUse (bool, 1 byte)
    1: None,                       # type (int, 4 bytes)
    5: kStringType,                # nameId (int, 4 bytes)
    9: kProperty,                  # prevPropId (int, 4 bytes)
    13: kProperty,                 # nextPropId (int, 4 bytes)
    17: (kStringType, kArrayType)  # propBlockId (4 bytes: data, strId, arrayId)
}

RelationshipOffsetReferenceMap = {
    0: None,               # inUse_direction (bool, 1 byte)
    1: kNode,              # firstNode (int, 4 bytes)
    5: kNode,              # secondNode (int, 4 bytes)
    9: kGeneralType,       # generalType (int, 4 bytes)
    13: kRelationship,     # firstPrevRelId (int, 4 bytes)
    17: kRelationship,     # firstNextRelId (int, 4 bytes)
    21: kRelationship,     # secondPrevRelId (int, 4 bytes)
    25: kRelationship,     # secondNextRelId (int, 4 bytes)
    29: kProperty,         # nextPropId (int, 4 bytes)
}

# ---------------------------- Type -> Offset Maps --------------------------- #
# ** Reference maps denote the types that these types reference, not
# ** what types references these types.

ArrayTypeReferenceMap = {
    kArrayType: [2, 14],
    kStringType: [18],
}

GeneralTypeReferenceMap = {
    kStringType: [1],
    kGeneralTypeType: [5],
}

GeneralTypeTypeReferenceMap = {
    kStringType: [1],
    kGeneralTypeType: [9],
}

StringTypeReferenceMap = {
    kStringType: [1, 9],
}

NodeTypeReferenceMap = {
    kRelationship: [1],
    kProperty: [5],
    kGeneralType: [9],
}

PropertyTypeReferenceMap = {
    kStringType: [5],
    kProperty: [9, 13],
    kPayload: [kPropertyPayloadOffset],
}

RelationshipTypeReferenceMap = {
    kNode: [1, 5],
    kGeneralType: [9],
    kRelationship: [13, 17, 21, 25],
    kProperty: [29],
}

TypeReferenceMap = {
    kArrayType: ArrayTypeReferenceMap,
    kGeneralType: GeneralTypeReferenceMap,
    kGeneralTypeType: GeneralTypeTypeReferenceMap,
    kStringType: StringTypeReferenceMap,
    kNode: NodeTypeReferenceMap,
    kProperty: PropertyTypeReferenceMap,
    kRelationship: RelationshipTypeReferenceMap,
}
