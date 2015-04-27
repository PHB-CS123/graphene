from graphene.storage import *

from graphene.storage.intermediate import *
from pylru import WriteBackCacheManager


class StorageManager:

    MAX_CACHE_SIZE = 100
    PROP_STORE_NAMES_FILENAME = "graphenestore.propertystore.db.strings"
    TYPE_STORE_FILENAME = "graphenestore.typestore.db"
    TYPE_STORE_NAMES_FILENAME = "graphenestore.typestore.db.names"
    TYPE_TYPE_STORE_FILENAME = "graphenestore.typetypestore.db"
    TYPE_TYPE_STORE_NAMES_FILENAME = "graphenestore.typetypestore.db.names"

    def __init__(self):
        self.node_manager = GeneralStoreManager(NodeStore())
        self.property_manager = GeneralStoreManager(PropertyStore())
        self.relationship_manager = GeneralStoreManager(RelationshipStore())

        nodeprop = NodePropertyStore(self.node_manager, self.property_manager)
        relprop = RelationshipPropertyStore(self.relationship_manager, self.property_manager)
        self.nodeprop = WriteBackCacheManager(nodeprop, self.MAX_CACHE_SIZE)
        self.relprop = WriteBackCacheManager(relprop, self.MAX_CACHE_SIZE)

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

        self.prop_string_manager = \
            GeneralNameManager(self.PROP_STORE_NAMES_FILENAME, 32)

    def create_type(self, type_name, schema):
        if self.type_name_manager.find_name(type_name) is not None:
            # The type name already exists!
            # TODO: Specific exception should go here
            raise Exception("Type %s already exists!" % type_name)
        name_index = self.type_name_manager.write_name(type_name)
        ids = self.type_type_manager.get_indexes(len(schema))
        # The reason we reverse the schema is so that when we create the linked
        # list, the type-types come out in order; i.e. when we select the first
        # one, it is indeed the same as the first one specified in the create
        # statement.
        for i, idx in enumerate(ids):
            tt_name, tt_type = schema[i]
            tt_name_id = self.type_type_name_manager.write_name(tt_name)
            kwargs = {
                "property_type": Property.PropertyType[tt_type],
                "type_name": tt_name_id,
                "index": idx
            }
            if i < len(ids) - 1:
                kwargs["next_type"] = ids[i + 1]
            prop = self.type_type_manager.create_item(**kwargs)
            self.type_type_manager.write_item(prop)
            # Store the most recently used index so that we can use it to chain
            # onto the linked list
            last_prop_id = prop.index
        new_type = self.type_manager.create_item(first_type=ids[0],
                                                name_id=name_index)
        self.type_manager.write_item(new_type)
        return new_type

    def delete_type_type(self, type_type):
        self.type_type_name_manager.delete_name_at_index(type_type.typeName)
        self.type_type_manager.delete_item(type_type)

    def delete_type(self, type_name):
        type_data, type_schema = self.get_type_data(type_name)
        for tt, _, __ in type_schema:
            self.delete_type_type(tt)
        for node in self.get_nodes_of_type(type_data):
            del self.nodeprop[node.index]
        self.nodeprop.sync() # Sync nodeprop cache
        self.type_name_manager.delete_name_at_index(type_data.nameId)
        self.type_manager.delete_item(type_data)

    def get_type_data(self, type_name):
        """
        Get the Type information (specifically, id) and schema given a Type name
        """
        idx = 1
        cur_type = None
        while True:
            cur_type = self.type_manager.get_item_at_index(idx)
            if cur_type is GeneralStore.EOF:
                cur_type = None
                break
            if cur_type is not None and \
                self.type_name_manager.read_name_at_index(cur_type.nameId) == type_name:
                break
            idx += 1
        if cur_type is None:
            # TODO: Create custom error here
            raise NameError("Type %s does not exist." % type_name)
        cur_type_type_id = cur_type.firstType
        schema = []
        while cur_type_type_id != 0:
            cur_type_type = self.type_type_manager.get_item_at_index(cur_type_type_id)
            cur_type_type_name = self.type_type_name_manager \
                                    .read_name_at_index(cur_type_type.typeName)
            schema.append((cur_type_type, cur_type_type_name, cur_type_type.propertyType))
            cur_type_type_id = cur_type_type.nextType
        return cur_type, schema

    def insert_node(self, node_type, node_properties):
        prop_ids = self.property_manager.get_indexes(len(node_properties))
        properties = []
        for i, idx in enumerate(prop_ids):
            prop_type, prop_val = node_properties[i]
            kwargs = {
                "index": idx,
                "prop_type": prop_type
            }
            if i > 0:
                kwargs["prev_prop_id"] = prop_ids[i - 1]
            if i < len(prop_ids) - 1:
                kwargs["next_prop_id"] = prop_ids[i + 1]

            if prop_type == Property.PropertyType.string:
                kwargs["prop_block_id"] = self.prop_string_manager.write_name(prop_val)
            else:
                kwargs["prop_block_id"] = prop_val
            stored_prop = self.property_manager.create_item(**kwargs)
            properties.append(stored_prop)
        new_node = self.node_manager.create_item(prop_id=prop_ids[0],
            node_type=node_type.index)
        self.nodeprop[new_node.index] = (new_node, properties)
        self.nodeprop.sync()
        return self.nodeprop[new_node.index]

    def get_node_type(self, node):
        return self.type_manager.get_item_at_index(node.nodeType)

    def get_property_value(self, prop):
        if prop.type == Property.PropertyType.string:
            return self.prop_string_manager.read_name_at_index(prop.propBlockId)
        return prop.propBlockId

    def get_node(self, index):
        nodeprop = self.nodeprop[index]
        if nodeprop is None or nodeprop == GeneralStore.EOF:
            return nodeprop
        node, properties = nodeprop
        node_type = self.type_manager.get_item_at_index(node.nodeType)
        type_name = self.type_name_manager.read_name_at_index(node_type.nameId)
        properties = map(self.get_property_value, properties)
        return NodeProperty(node, properties, node_type, type_name)

    def get_nodes_of_type(self, node_type):
        i = 1
        while True:
            node = self.get_node(i)
            if node == GeneralStore.EOF:
                break
            i += 1
            if node is not None and node.type == node_type:
                yield node

    def convert_to_value(self, s, given_type):
        if given_type == Property.PropertyType.bool:
            if s.upper() == "TRUE":
                return True
            return False
        if given_type == Property.PropertyType.int:
            return int(s)
        if given_type == Property.PropertyType.string:
            return s[1:-1]
