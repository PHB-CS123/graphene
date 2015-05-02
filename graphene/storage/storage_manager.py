from graphene.storage import *
from graphene.errors.storage_manager_errors import *

from graphene.storage.intermediate import *
from pylru import WriteBackCacheManager

from pdb import set_trace

class StorageManager:
    # Maximum size of the cache (in items)
    MAX_CACHE_SIZE = 100

    # Filename for the node type store
    NODE_TYPE_STORE_FILENAME = "graphenestore.nodetypestore.db"
    # Filename for the dynamic name manager for node type names store
    NODE_TYPE_STORE_NAMES_FILENAME = "graphenestore.nodetypestore.db.names"
    # Filename for the store manager for types of node types
    NODE_TYPE_TYPE_STORE_FILENAME = "graphenestore.nodetypestore.types.db"
    # Filename for the dynamic name manager for types of node types
    NODE_TYPE_TYPE_STORE_NAMES_FILENAME = \
        "graphenestore.nodetypestore.types.db.names"

    # Filename for the relationship type store
    RELATIONSHIP_TYPE_STORE_FILENAME = "graphenestore.relationshiptypestore.db"
    # Filename for the dynamic name manager for relationship type names store
    RELATIONSHIP_TYPE_STORE_NAMES_FILENAME = \
        "graphenestore.relationshiptypestore.db.names"
    # Filename for the store manager for types of relationship types
    RELATIONSHIP_TYPE_TYPE_STORE_FILENAME = \
        "graphenestore.relationshiptypestore.types.db"
    # Filename for the dynamic name manager for types of relationship types
    RELATIONSHIP_TYPE_TYPE_STORE_NAMES_FILENAME = \
        "graphenestore.relationshiptypestore.types.db.names"

    # Filename for the dynamic string property manager
    PROP_STORE_STRINGS_FILENAME = "graphenestore.propertystore.db.strings"

    # Size of name blocks
    NAME_BLOCK_SIZE = 10
    # Size of string blocks
    STRING_BLOCK_SIZE = 32

    def __init__(self):
        """
        Initialize all the required storage managers

        :return: StoreManager instance to handle general storage manipulations
        :rtype: StorageManager
        """
        # Create object managers
        self.node_manager = GeneralStoreManager(NodeStore())
        self.property_manager = GeneralStoreManager(PropertyStore())
        self.relationship_manager = GeneralStoreManager(RelationshipStore())

        # Create combined object managers along with their cache handlers
        nodeprop = NodePropertyStore(self.node_manager, self.property_manager)
        relprop = RelationshipPropertyStore(self.relationship_manager,
                                            self.property_manager)
        self.nodeprop = WriteBackCacheManager(nodeprop, self.MAX_CACHE_SIZE)
        self.relprop = WriteBackCacheManager(relprop, self.MAX_CACHE_SIZE)

        # --- Node type stores, and name stores --- #
        # Create store and manager for node types
        node_type_store = GeneralTypeStore(self.NODE_TYPE_STORE_FILENAME)
        self.nodeTypeManager = GeneralStoreManager(node_type_store)
        # Create a manager for node type names
        self.nodeTypeNameManager = \
            GeneralNameManager(self.NODE_TYPE_STORE_NAMES_FILENAME,
                               self.NAME_BLOCK_SIZE)
        # Create store and manager for types of node types
        node_tt_store = GeneralTypeTypeStore(self.NODE_TYPE_TYPE_STORE_FILENAME)
        self.nodeTypeTypeManager = GeneralStoreManager(node_tt_store)
        # Create a manager for names of types of node types
        self.nodeTypeTypeNameManager = \
            GeneralNameManager(self.NODE_TYPE_TYPE_STORE_NAMES_FILENAME,
                               self.NAME_BLOCK_SIZE)

        # --- Relationship type stores, and name stores --- #
        # Create store and manager for relationship types
        rel_type_store = GeneralTypeStore(self.RELATIONSHIP_TYPE_STORE_FILENAME)
        self.relTypeManager = GeneralStoreManager(rel_type_store)
        # Create a manager for relationship type names
        self.relTypeNameManager = \
            GeneralNameManager(self.RELATIONSHIP_TYPE_STORE_NAMES_FILENAME,
                               self.NAME_BLOCK_SIZE)
        # Create store and manager for types of relationship types
        relationship_tt_store = \
            GeneralTypeTypeStore(self.RELATIONSHIP_TYPE_TYPE_STORE_FILENAME)
        self.relTypeTypeManager = GeneralStoreManager(relationship_tt_store)
        # Create a manager for names of types of relationship types
        self.relTypeTypeNameManager = \
            GeneralNameManager(self.RELATIONSHIP_TYPE_TYPE_STORE_NAMES_FILENAME,
                               self.NAME_BLOCK_SIZE)

        # Create a string manager for string property types
        self.prop_string_manager = \
            GeneralNameManager(self.PROP_STORE_STRINGS_FILENAME,
                               self.STRING_BLOCK_SIZE)

    # --- Node Storage Methods --- #

    def create_node_type(self, type_name, schema):
        """
        Wrapper around create_type for nodes

        :param type_name: Name of node type
        :type type_name: str
        :param schema: Schema for node type
        :type schema: tuple
        :return: Index of Newly created node type
        """
        return self.create_type(type_name, schema, True)

    def delete_node_type(self, type_name):
        """
        Wrapper around delete_type for nodes

        :param type_name: Name of node type to delete
        :type type_name: str
        :return Nothing
        :rtype None
        """
        self.delete_type(type_name, True)

    def get_node_data(self, type_name):
        """
        Wrapper around get_type_data for nodes

        :param type_name: Name of node type to retrieve data for
        :type type_name: str
        :return: ID and schema for node type with given name
        :rtype: tuple
        """
        return self.get_type_data(type_name, True)

    # --- Relationship Storage Methods --- #

    def create_relationship_type(self, type_name, schema):
        """
        Wrapper around create_type for relationships

        :param type_name: Name of re type
        :type type_name: str
        :param schema: Schema for node type
        :type schema: tuple
        :return: Index of Newly created node type
        """
        return self.create_type(type_name, schema, False)

    def delete_relationship_type(self, type_name):
        """
        Wrapper around delete_type for relationships

        :param type_name: Name of relationship type to delete
        :type type_name: str
        :return Nothing
        :rtype None
        """
        self.delete_type(type_name, False)

    def get_relationship_data(self, type_name):
        """
        Wrapper around get_type_data for relationships

        :param type_name: Name of relationship type to retrieve data for
        :type type_name: str
        :return: ID and schema for relationship type with given name
        :rtype: tuple
        """
        return self.get_type_data(type_name, False)

    # --- Private Storage Methods --- #

    def create_type(self, type_name, schema, node_flag):
        """
        Creates a node or relationship type with the given name and schema

        :param type_name: Name of type
        :type type_name: str
        :param schema: Schema for type
        :type schema: tuple
        :param node_flag: Flag specifying whether we are adding a node type
                          (True) or a relationship type (False)
        :type node_flag: bool
        :return: Index of Newly created type
        """
        # Get the appropriate managers
        # Creating a node type
        if node_flag is True:
            type_manager = self.nodeTypeManager
            type_name_manager = self.nodeTypeNameManager
            type_type_manager = self.nodeTypeTypeManager
            type_type_name_manager = self.nodeTypeTypeNameManager
        # Creating a relationship type
        else:
            type_manager = self.relTypeManager
            type_name_manager = self.relTypeNameManager
            type_type_manager = self.relTypeTypeManager
            type_type_name_manager = self.relTypeTypeNameManager

        if type_name_manager.find_name(type_name) is not None:
            # The type name already exists!
            raise TypeAlreadyExistsException(
                "Type %s already exists!" % type_name)
        name_index = type_name_manager.write_name(type_name)
        if len(schema) > 0:
            ids = type_type_manager.get_indexes(len(schema))
            # Create linked list of types for the created type
            for i, idx in enumerate(ids):
                tt_name, tt_type = schema[i]
                tt_name_id = type_type_name_manager.write_name(tt_name)
                kwargs = {
                    "property_type": Property.PropertyType[tt_type],
                    "type_name": tt_name_id,
                    "index": idx
                }
                if i < len(ids) - 1:
                    kwargs["next_type"] = ids[i + 1]
                prop = type_type_manager.create_item(**kwargs)
                type_type_manager.write_item(prop)
            new_type = type_manager.create_item(first_type=ids[0],
                                                name_id=name_index)
        else:
            new_type = type_manager.create_item(name_id=name_index)
        type_manager.write_item(new_type)
        print("type manager wrote new type: %s" % new_type)
        return new_type

    def delete_type_type(self, type_type, node_flag):
        """
        Deletes the given type of a node or relationship type

        :param type_type: Type of node or relationship type to delete
        :type type_type: GeneralTypeType
        :param node_flag: Flag specifying whether we are deleting a type of a
                          node type (True) or a relationship type (False)
        :type node_flag: bool
        :return: Nothing
        :rtype: None
        """
        # Get the appropriate managers
        # Deleting a node type type
        if node_flag is True:
            type_type_manager = self.nodeTypeTypeManager
            type_type_name_manager = self.nodeTypeTypeNameManager
        # Deleting a relationship type type
        else:
            type_type_manager = self.relTypeTypeManager
            type_type_name_manager = self.relTypeTypeNameManager

        type_type_name_manager.delete_name_at_index(type_type.typeName)
        type_type_manager.delete_item(type_type)

    def delete_type(self, type_name, node_flag):
        """
        Deletes the node or relationship type with the given name

        :param type_name: Name of type to delete
        :type type_name: str
        :param node_flag: Flag specifying whether we are deleting a node type
                          (True) or a relationship type (False)
        :type node_flag: bool
        :return Nothing
        :rtype None
        """
        # Get the appropriate managers
        # Deleting a node type
        if node_flag is True:
            cache = self.nodeprop
            type_manager = self.nodeTypeManager
            type_name_manager = self.nodeTypeNameManager
        # Deleting a relationship type
        else:
            cache = self.relprop
            type_manager = self.relTypeManager
            type_name_manager = self.relTypeNameManager

        type_data, type_schema = self.get_type_data(type_name, node_flag)
        for tt, _, __ in type_schema:
            self.delete_type_type(tt, node_flag)
        for node in self.get_nodes_of_type(type_data):
            del cache[node.index]
        cache.sync()  # Sync nodeprop cache
        type_name_manager.delete_name_at_index(type_data.nameId)
        type_manager.delete_item(type_data)

    def get_type_data(self, type_name, node_flag):
        """
        Get the Type information (specifically, id) and schema given a Type name

        :param type_name: Name of type to retrieve data for
        :type type_name: str
        :param node_flag: Flag specifying whether we are getting data for
                          a node type (True) or a relationship type (False)
        :type node_flag: bool
        :return: ID and schema for type with given name
        :rtype: tuple
        """
        # Get the appropriate managers
        # Getting data for a node
        if node_flag is True:
            type_manager = self.nodeTypeManager
            type_name_manager = self.nodeTypeNameManager
            type_type_manager = self.nodeTypeTypeManager
            type_type_name_manager = self.nodeTypeTypeNameManager
        # Getting data for a relationship
        else:
            type_manager = self.relTypeManager
            type_name_manager = self.relTypeNameManager
            type_type_manager = self.relTypeTypeManager
            type_type_name_manager = self.relTypeTypeNameManager

        idx = 1
        cur_type = None
        while True:
            cur_type = type_manager.get_item_at_index(idx)
            if cur_type is GeneralStore.EOF:
                cur_type = None
                break
            if cur_type is not None and \
               type_name_manager.read_name_at_index(cur_type.nameId) == type_name:
                break
            idx += 1
        if cur_type is None:
            # Invalid type name
            raise TypeDoesNotExistException(
                "Type %s does not exist." % type_name)
        cur_type_type_id = cur_type.firstType
        schema = []
        while cur_type_type_id != 0:
            cur_type_type = type_type_manager.get_item_at_index(cur_type_type_id)
            cur_type_type_name = type_type_name_manager\
                .read_name_at_index(cur_type_type.typeName)
            schema.append(
                (cur_type_type, cur_type_type_name, cur_type_type.propertyType))
            cur_type_type_id = cur_type_type.nextType
        return cur_type, schema

    # --- Node Specific Storage Methods --- #
    # TODO: generalize the rest of the functions for relationships as well
    def insert_node(self, node_type, node_properties):
        properties = []
        if len(node_properties) > 0:
            prop_ids = self.property_manager.get_indexes(len(node_properties))
            print("Node properties: %s" % (node_properties,))
            for i, idx in enumerate(prop_ids):
                prop_type, prop_val = node_properties[i]
                kwargs = {
                    "index": idx,
                    "prop_type": prop_type
                }
                if i > 0:
                    kwargs["prev_prop_id"] = prop_ids[i - 1]
                elif i < len(prop_ids) - 1:
                    kwargs["next_prop_id"] = prop_ids[i + 1]

                if prop_type == Property.PropertyType.string:
                    kwargs["prop_block_id"] = \
                        self.prop_string_manager.write_name(prop_val)
                else:
                    kwargs["prop_block_id"] = prop_val
                stored_prop = self.property_manager.create_item(**kwargs)
                properties.append(stored_prop)
            print("Final properties: %s" % (node_properties,))
            new_node = self.node_manager.create_item(prop_id=prop_ids[0],
                                                     node_type=node_type.index)
        else:
            new_node = self.node_manager.create_item(node_type=node_type.index)
        # Update cache with new values and sync with store
        self.nodeprop[new_node.index] = (new_node, properties)
        self.nodeprop.sync()
        return (new_node, properties)

    def get_node_type(self, node):
        return self.nodeTypeManager.get_item_at_index(node.nodeType)

    def get_property_value(self, prop):
        if prop.type == Property.PropertyType.string:
            return self.prop_string_manager.read_name_at_index(prop.propBlockId)
        return prop.propBlockId

    def get_node(self, index):
        nodeprop = self.nodeprop[index]
        if nodeprop is None or nodeprop == GeneralStore.EOF:
            return nodeprop
        node, properties = nodeprop
        node_type = self.nodeTypeManager.get_item_at_index(node.nodeType)
        type_name = self.nodeTypeNameManager.\
            read_name_at_index(node_type.nameId)
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

    def insert_relation(self, rel_type, rel_properties, src_node, dst_node):
        """
        Creates a directed relationship (rel_type) from src_node to dst_node.

        :param rel_type: details of the relationship
        :param rel_properties: labels on the relationship, for example
                               R(year = 1995)
        :param src_node: node that points
        :param dst_node: node that is pointed to
        :return: (relationship, properties)
        """
        properties = []
        if rel_properties:
            prop_ids = self.property_manager.get_indexes(len(rel_properties))
            for i, idx in enumerate(prop_ids):
                prop_type, prop_val = rel_properties[i]
                prop_kwargs = {
                    "index": idx,
                    "prop_type": prop_type
                }
                if i > 0:
                    prop_kwargs["prev_prop_id"] = prop_ids[i - 1]
                elif i < len(prop_ids) - 1:
                    prop_kwargs["next_prop_id"] = prop_ids[i + 1]

                if prop_type == Property.PropertyType.string:
                    prop_kwargs["prop_block_id"] = \
                    # TODO: Why are new relation property names not getting
                    # written?
                        self.prop_string_manager.write_name(prop_val)
                else:
                    prop_kwargs["prop_block_id"] = prop_val
                stored_prop = self.property_manager.create_item(**prop_kwargs)
                properties.append(stored_prop)
            print("Final properties: %s" % (rel_properties,))
            # new_rel = self.relationship_manager.create_item(
            #     prop_id=prop_ids[0], rel_type=rel_type.index)
        # else:
        #     new_rel = self.relationship_manager.create_item(rel_type=rel_type.index)


        # TODO: Relationship's first prop_id is 0 if it has no properties?
        first_prop_idx = properties[0].index if rel_properties else 0

        # Just get one index for this relationship
        rel_idx = self.relationship_manager.get_indexes(1)[0]

        # TODO: Handle setting previous rel IDs and propID
        rel_kwargs = {
            "index": rel_idx,
            "direction": Relationship.Direction.right,
            "first_node_id": src_node.node.index,
            "second_node_id": dst_node.node.index,
            "rel_type": rel_type.index,
            "prop_id": first_prop_idx
        }
        new_rel = self.relationship_manager.create_item(**rel_kwargs)

        self.relprop[new_rel.index] = (new_rel, properties)
        self.relprop.sync()
        # Only do this if it's their first relation
        # src_node.node.relId = new_rel.index
        # dst_node.node.relId

        print("new rel: %s" % new_rel)
        return

    @staticmethod
    def convert_to_value(s, given_type):
        if given_type == Property.PropertyType.bool:
            if s.upper() == "TRUE":
                return True
            return False
        if given_type == Property.PropertyType.int:
            return int(s)
        if given_type == Property.PropertyType.string:
            return s[1:-1]
