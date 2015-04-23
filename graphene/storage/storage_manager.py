from graphene.storage import *

from graphene.storage.intermediate import *
from pylru import WriteBackCacheManager


class StorageManager:

    MAX_CACHE_SIZE = 100
    TYPE_STORE_FILENAME = "graphenestore.typestore.db"
    TYPE_STORE_NAMES_FILENAME = "graphenestore.typestore.db.names"
    TYPE_TYPE_STORE_FILENAME = "graphenestore.typetypestore.db"
    TYPE_TYPE_STORE_NAMES_FILENAME = "graphenestore.typetypestore.db.names"

    def __init__(self):
        node_manager = GeneralStoreManager(NodeStore())
        property_manager = GeneralStoreManager(PropertyStore())
        relationship_manager = GeneralStoreManager(RelationshipStore())

        self.nodeprop = NodePropertyStore(node_manager, property_manager)
        self.relprop = RelationshipPropertyStore(relationship_manager, property_manager)

        type_store = GeneralTypeStore(self.TYPE_STORE_FILENAME)
        self.type_manager = GeneralStoreManager(type_store)

        type_type_store = GeneralTypeTypeStore(self.TYPE_TYPE_STORE_FILENAME)
        self.type_type_manager = GeneralStoreManager(type_type_store)

        # relationship_manager = GeneralStoreManager(RelationshipStore)
        # relationship_type_manager = GeneralStoreManager(RelationshipTypeStore)

        self.type_name_manager = \
            GeneralNameManager(self.TYPE_STORE_NAMES_FILENAME, 10)
        self.type_type_name_manager = \
            GeneralNameManager(self.TYPE_TYPE_STORE_NAMES_FILENAME, 10)

    def create_type(self, type_name, schema):
        if self.type_name_manager.find_name(type_name) is not None:
            # The type name already exists!
            # TODO: Specific exception should go here
            raise Exception("Type %s already exists!" % type_name)
        name_index = self.type_name_manager.write_name(type_name)
        last_prop_id = 0
        # The reason we reverse the schema is so that when we create the linked
        # list, the type-types come out in order; i.e. when we select the first
        # one, it is indeed the same as the first one specified in the create
        # statement.
        for tt_name, tt_type in schema[::-1]:
            tt_name_id = self.type_type_name_manager.write_name(tt_name)
            prop = self.type_type_manager \
                    .create_item(property_type=Property.PropertyType[tt_type],
                                 next_type=last_prop_id, type_name=tt_name_id)
            self.type_type_manager.write_item(prop)
            # Store the most recently used index so that we can use it to chain
            # onto the linked list
            last_prop_id = prop.index
        new_type = self.type_manager.create_item(first_type=last_prop_id,
                                                name_id=name_index)
        self.type_manager.write_item(new_type)
        return new_type
