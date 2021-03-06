from pylru import WriteBackCacheManager
import logging

from graphene.errors.storage_manager_errors import *
from graphene.errors.query_errors import NonexistentPropertyException
from graphene.storage import *
from graphene.storage.base.property import Property
from graphene.storage.intermediate import *
from graphene.storage.defrag.defrag_helpers import *

class StorageManager:
    # Maximum size of the cache (in items)
    MAX_CACHE_SIZE = 10000

    # Filename for the node type store
    NODE_TYPE_STORE_FILENAME = "graphenestore.nodetypestore.db"
    # Filename for the dynamic name manager for node type names store
    NODE_TYPE_STORE_NAMES_FILENAME = "graphenestore.nodetypestore.names.db"
    # Filename for the store manager for types of node types
    NODE_TYPE_TYPE_STORE_FILENAME = "graphenestore.nodetypestore.types.db"
    # Filename for the dynamic name manager for types of node types
    NODE_TYPE_TYPE_STORE_NAMES_FILENAME = \
        "graphenestore.nodetypestore.types.names.db"

    # Filename for the relationship type store
    RELATIONSHIP_TYPE_STORE_FILENAME = "graphenestore.relationshiptypestore.db"
    # Filename for the dynamic name manager for relationship type names store
    RELATIONSHIP_TYPE_STORE_NAMES_FILENAME = \
        "graphenestore.relationshiptypestore.names.db"
    # Filename for the store manager for types of relationship types
    RELATIONSHIP_TYPE_TYPE_STORE_FILENAME = \
        "graphenestore.relationshiptypestore.types.db"
    # Filename for the dynamic name manager for types of relationship types
    RELATIONSHIP_TYPE_TYPE_STORE_NAMES_FILENAME = \
        "graphenestore.relationshiptypestore.types.names.db"

    # Filename for the dynamic string property manager
    PROP_STORE_STRINGS_FILENAME = "graphenestore.propertystore.strings.db"

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
        self.logger = logging.getLogger(self.__class__.__name__)

        # Create a string manager for string property types
        self.prop_string_manager = \
            GeneralStringManager(self.PROP_STORE_STRINGS_FILENAME,
                                 self.STRING_BLOCK_SIZE)

        # Create object managers
        self.node_manager = GeneralStoreManager(NodeStore())
        self.property_manager = GeneralStoreManager(PropertyStore())
        self.relationship_manager = GeneralStoreManager(RelationshipStore())
        self.array_manager = GeneralArrayManager()

        # Create combined object managers along with their cache handlers
        nodeprop = NodePropertyStore(self)
        relprop = RelationshipPropertyStore(self)
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

    def __del__(self):
        self.close()

    def close(self):
        # Delete the property string manager
        del self.prop_string_manager

        # Delete the caches
        del self.nodeprop
        del self.relprop

        # Delete the base managers
        del self.node_manager
        del self.property_manager
        del self.relationship_manager
        del self.array_manager

        # Delete the node type managers
        del self.nodeTypeManager
        del self.nodeTypeNameManager

        # Delete the node type-type managers
        del self.nodeTypeTypeManager
        del self.nodeTypeTypeNameManager

        # Delete the relation type managers
        del self.relTypeManager
        del self.relTypeNameManager

        # Delete the relation type-type managers
        del self.relTypeTypeManager
        del self.relTypeTypeNameManager

# --- Node Storage Interface Methods --- #

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

# --- Relationship Storage Interface Methods --- #

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

# --- Type Storage Methods --- #

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

        # Make sure the type does not already exists
        if type_name_manager.find_string(type_name) is not None:
            # The type name already exists!
            if node_flag:
                raise TypeAlreadyExistsException(
                    "Type %s already exists!" % type_name)
            else:
                raise TypeAlreadyExistsException(
                    "Relation %s already exists!" % type_name)
        name_index = type_name_manager.write_string(type_name)

        if len(schema) > 0:
            ids = type_type_manager.get_indexes(len(schema))
            # Create linked list of types for the created type
            for i, idx in enumerate(ids):
                tt_name, tt_type = schema[i]
                # Replace array syntax with Array following the array type
                if tt_type.find("[]") > -1:
                    tt_type = tt_type.replace("[]", "Array")
                tt_name_id = type_type_name_manager.write_string(tt_name)
                kwargs = {
                    "property_type": Property.PropertyType[tt_type],
                    "type_name": tt_name_id,
                    "index": idx
                }
                if i < len(ids) - 1:
                    kwargs["next_type"] = ids[i + 1]
                prop = type_type_manager.create_item(**kwargs)
            new_type = type_manager.create_item(first_type=ids[0],
                                                name_id=name_index)
        else:
            new_type = type_manager.create_item(name_id=name_index)
        self.logger.debug("TypeManager wrote new type: %s" % new_type)
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

        if type_type.propertyType == Property.PropertyType.string:
            # TODO: Need to delete all strings of this type_type in the
            # prop_string_manager.

            # Note: type_type.typeName is the index of the type name in node type
            # type name manager, so the following does not suffice.
            # self.prop_string_manager.delete_string_at_index(type_type.typeName)
            pass
        # TODO: same for array type_type

        type_type_name_manager.delete_string_at_index(type_type.typeName)
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
        type_name_manager.delete_string_at_index(type_data.nameId)
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
               type_name_manager.read_string_at_index(cur_type.nameId) == type_name:
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
                .read_string_at_index(cur_type_type.typeName)
            schema.append(
                (cur_type_type, cur_type_type_name, cur_type_type.propertyType))
            cur_type_type_id = cur_type_type.nextType
        return cur_type, schema

# --- Node Specific Storage Methods --- #
    def insert_node(self, node_type, node_properties):
        """
        Inserts a node with the given type and properties

        :param node_type: Type of node
        :type node_type: GeneralType
        :param node_properties: List of tuples containing (PropertyType, Value)
        :type node_properties: tuple
        :return: ID of new node and the IDs of the properties of the node
        :rtype: tuple
        """
        properties = []
        if len(node_properties) > 0:
            # Get the needed number of IDs to store the properties
            prop_ids = self.property_manager.get_indexes(len(node_properties))
            self.logger.debug("Node properties: %s" % (node_properties,))
            # Store all the properties
            for i, idx in enumerate(prop_ids):
                # Get current property type and value for the type
                prop_type, prop_val = node_properties[i]
                kwargs = self.generate_property_args(idx, prop_type, prop_val)
                # Non edge cases, prop_ids non-zero
                if i > 0:
                    kwargs["prev_prop_id"] = prop_ids[i - 1]
                if i < len(prop_ids) - 1:
                    kwargs["next_prop_id"] = prop_ids[i + 1]

                # String, so write name
                if prop_type == Property.PropertyType.string:
                    kwargs["prop_block_id"] = \
                        self.prop_string_manager.write_string(prop_val)
                # Array, so use array manager
                elif prop_type.value >= Property.PropertyType.intArray.value:
                    kwargs["prop_block_id"] = \
                        self.array_manager.write_array(prop_val, prop_type)
                # Otherwise primitive
                else:
                    kwargs["prop_block_id"] = prop_val
                # Create property and add it to the list of properties
                stored_prop = self.property_manager.create_item(**kwargs)
                properties.append(stored_prop)
            self.logger.debug("Final properties: %s" % (node_properties,))
            # Create node with the ID of first property and index of node type
            new_node = self.node_manager.create_item(prop_id=prop_ids[0],
                                                     node_type=node_type.index)
        # Node with no properties
        else:
            new_node = self.node_manager.create_item(node_type=node_type.index)
        # Update cache with new values and sync with store
        self.nodeprop[new_node.index] = (new_node, properties)
        self.nodeprop.sync()
        return (new_node, properties)

    def get_node_type(self, node):
        """
        Get the type of the given node

        :param node: Node to get type for
        :type node: Node
        :return: Node type for node
        :rtype: GeneralType
        """
        return self.nodeTypeManager.get_item_at_index(node.nodeType)

    def get_property_value(self, prop):
        """
        Gets the data value for the given property

        :param prop: Property to get value for
        :type prop: Property
        :return: Value
        :rtype: Any
        """
        if prop.type == Property.PropertyType.string:
            return self.prop_string_manager.read_string_at_index(prop.propBlockId)
        elif prop.type.value >= Property.PropertyType.intArray.value:
            return self.array_manager.read_array_at_index(prop.propBlockId)
        else:
            return prop.propBlockId

    def get_node(self, index):
        """
        Gets the NodeProperty at the given index
        :param index: Index of node
        :type index: int
        :return: NodeProperty at given node index
        :rtype: NodeProperty
        """
        nodeprop = self.nodeprop[index]
        if nodeprop is None or nodeprop == GeneralStore.EOF:
            return nodeprop
        node, properties = nodeprop
        node_type = self.nodeTypeManager.get_item_at_index(node.nodeType)
        type_name = self.nodeTypeNameManager.\
            read_string_at_index(node_type.nameId)
        properties = map(self.get_property_value, properties)
        return NodeProperty(node, properties, node_type, type_name)

    def get_nodes_of_type(self, node_type):
        """
        Get NodeProperty items of the given type. Generator

        :param node_type: Type index of node
        :type node_type: int
        :return: NodeProperty generator
        :rtype: list[NodeProperty]
        """
        i = 1
        while True:
            node = self.get_node(i)
            if node == GeneralStore.EOF:
                break
            i += 1
            if node is not None and node.type == node_type:
                yield node

# --- Relationship Specific Storage Methods --- #
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
                if i < len(prop_ids) - 1:
                    prop_kwargs["next_prop_id"] = prop_ids[i + 1]

                if prop_type == Property.PropertyType.string:
                    # set_trace()
                    # TODO: Why are new relation property names not getting
                    # written?
                    prop_kwargs["prop_block_id"] = \
                        self.prop_string_manager.write_string(prop_val)
                # array, so use array manager
                elif prop_type.value >= Property.PropertyType.intArray.value:
                    prop_kwargs["prop_block_id"] = \
                        self.array_manager.write_array(prop_val, prop_type)
                else:
                    prop_kwargs["prop_block_id"] = prop_val
                stored_prop = self.property_manager.create_item(**prop_kwargs)
                properties.append(stored_prop)
            self.logger.debug("Final properties: %s" % (rel_properties,))

        # TODO: Relationship's first prop_id is 0 if it has no properties?
        first_prop_idx = properties[0].index if rel_properties else 0

        # Just get one index for this relationship
        rel_idx = self.relationship_manager.get_indexes()[0]

        src_idx, dst_idx = src_node.index, dst_node.index

        rel_kwargs = {
            "index": rel_idx,
            "direction": Relationship.Direction.right,
            "first_node_id": src_idx,
            "second_node_id": dst_idx,
            "rel_type": rel_type.index,
            "prop_id": first_prop_idx
        }

        # Insert into source/destination nodes' relation linked lists
        if src_node.relId > 0:
            # If source node already has a relation ID, we have to properly
            # shift them. That means we update the original first relationship
            # to say that this new one is the previous one for this given node,
            # and add a next ID to this one of the original relationship.
            orig_rel = self.relationship_manager.get_item_at_index(src_node.relId)
            if src_idx == orig_rel.firstNodeId:
                # THIS relationship's source is THE ORIGINAL'S source
                orig_rel.firstPrevRelId = rel_idx
                rel_kwargs["first_next_rel_id"] = orig_rel.index
            elif src_idx == orig_rel.secondNodeId:
                # THIS relationship's source is THE ORIGINAL'S destination
                orig_rel.secondPrevRelId = rel_idx
                rel_kwargs["first_next_rel_id"] = orig_rel.index

            # Note that we have to pull the properties out... this is so we
            # don't mess up the cache values
            self.relprop[src_node.relId] = (orig_rel, self.relprop[src_node.relId][1])
        if dst_node.relId > 0:
            # See above. Same deal with destinations
            orig_rel = self.relationship_manager.get_item_at_index(dst_node.relId)
            if dst_idx == orig_rel.firstNodeId:
                # THIS relationship's destination is THE ORIGINAL'S source
                orig_rel.firstPrevRelId = rel_idx
                rel_kwargs["second_next_rel_id"] = orig_rel.index
            elif dst_idx == orig_rel.secondNodeId:
                # THIS relationship's destination is THE ORIGINAL'S destination
                orig_rel.secondPrevRelId = rel_idx
                rel_kwargs["second_next_rel_id"] = orig_rel.index

            self.relprop[dst_node.relId] = (orig_rel, self.relprop[dst_node.relId][1])
        # Set src_node first relation ID to this
        # Note that we have to pull the properties out... this is so we don't
        # mess up the cache values
        src_node.relId = rel_idx
        self.nodeprop[src_idx] = (src_node, self.nodeprop[src_idx][1])
        # Set dst_node first relation ID to this
        dst_node.relId = rel_idx
        self.nodeprop[dst_idx] = (dst_node, self.nodeprop[dst_idx][1])

        self.nodeprop.sync()

        new_rel = self.relationship_manager.create_item(**rel_kwargs)

        self.relprop[new_rel.index] = (new_rel, properties)
        self.relprop.sync()
        self.logger.debug("New Relationship: %s" % new_rel)
        return new_rel

    def get_relation(self, index):
        relprop = self.relprop[index]
        if relprop is None or relprop == GeneralStore.EOF:
            return relprop
        rel, properties = relprop
        rel_type = self.relTypeManager.get_item_at_index(rel.relType)
        type_name = self.relTypeNameManager.\
            read_string_at_index(rel_type.nameId)
        properties = map(self.get_property_value, properties)
        return RelationProperty(rel, properties, rel_type, type_name)

    def get_relations_of_type(self, relation_type):
        i = 1
        while True:
            relation = self.get_relation(i)
            if relation == GeneralStore.EOF:
                break
            i += 1
            if relation is not None and relation.type == relation_type:
                yield relation

# --- Deletion Methods --- #
    def update_relation_links(self, node_id, prev_rel_id, next_rel_id):
        """
        Update the linked lists this relation was attached to for a given node
        (left node or right node)

        Three cases to handle:
        1.  Previous and next relation ID = 0: This was the only relation
            attached to the given node, so we don't have to do anything other
            than remove the node's reference to this relation.
        2.  Previous relation ID = 0: This was the first relation for the node,
            so make whatever was after this relation the first relation for the
            original node.
        3.  Both previous and next relations exist: We are in the middle of the
            list. Pop the relation from the linked list, reattaching the
            relations on either side together.
        """
        if prev_rel_id == 0:
            cur_node, cur_node_props = self.nodeprop[node_id]
            cur_node.relId = next_rel_id
            self.nodeprop[cur_node.index] = (cur_node, cur_node_props)
            self.nodeprop.sync()
            if next_rel_id != 0:
                # set next relation's previous relation to 0 (since it is now
                # the first relation of that node)
                next_rel, next_props = self.relprop[next_rel_id]
                if next_rel.firstNodeId == node_id:
                    next_rel.firstPrevRelId = 0
                else:
                    next_rel.secondPrevRelId = 0
                self.relprop[next_rel.index] = (next_rel, next_props)
                self.relprop.sync()
        else:
            # Set prev. relation's next rel to this relation's next rel.
            prev_rel, prev_props = self.relprop[prev_rel_id]
            if prev_rel.firstNodeId == node_id:
                prev_rel.firstNextRelId = next_rel_id
            else:
                prev_rel.secondNextRelId = next_rel_id
            self.relprop[prev_rel.index] = (prev_rel, prev_props)

            if next_rel_id != 0:
                # Set next relation's prev. rel to this relation's prev. rel
                next_rel, next_props = self.relprop[next_rel_id]
                if next_rel.firstNodeId == node_id:
                    next_rel.firstPrevRelId = prev_rel_id
                else:
                    next_rel.secondPrevRelId = prev_rel_id
                self.relprop[next_rel.index] = (next_rel, next_props)
            self.relprop.sync()

    def delete_relation(self, rel):
        """
        Deletes a relation and anything referencing it. Also makes sure to
        update linked lists that may have passed through this relation.
        """

        # Update the links between relations to ensure that the lists are
        # attached properly
        self.update_relation_links(rel.firstNodeId, rel.firstPrevRelId,
            rel.firstNextRelId)
        self.update_relation_links(rel.secondNodeId, rel.secondPrevRelId,
            rel.secondNextRelId)

        # Delete the properties the relation references
        cur_prop_id = rel.propId
        while cur_prop_id != 0:
            prop = self.property_manager.get_item_at_index(cur_prop_id)
            cur_prop_id = prop.nextPropId
            self.delete_property(prop)

        # Delete relation itself
        self.relationship_manager.delete_item(rel)

    def delete_property(self, prop):
        """
        Deletes a property and, if necessary, the string or array it references.
        """
        if prop.type == Property.PropertyType.string:
            # The property has a string type, so we have to make sure we delete
            # that string
            self.prop_string_manager.delete_string_at_index(prop.propBlockId)
        elif prop.type.value >= Property.PropertyType.intArray.value:
            # Property has an array type, so delete the array
            self.array_manager.delete_array_at_index(prop.propBlockId)

        # Delete property itself
        self.property_manager.delete_item(prop)

    def delete_node(self, node):
        """
        Deletes a node and everything that contains it as a reference.
        """

        # Delete all relations that are attached to this node (since they can't
        # be attached to nothing)
        cur_rel_id = node.relId
        isOnlyRel = False
        while cur_rel_id != 0:
            rel = self.relationship_manager.get_item_at_index(cur_rel_id)
            # Determine which list to pass through
            if rel.firstNodeId == node.index:
                cur_rel_id = rel.firstNextRelId
                isOnlyRel = rel.firstPrevRelId == 0
            else:
                cur_rel_id = rel.secondNextRelId
                isOnlyRel = rel.secondPrevRelId == 0
            # Delete the cache instance of the relation (will trigger proper
            # deletion of relation through storage manager too)
            del self.relprop[rel.index]
            self.relprop.sync()

        # Delete all properties referred to by this node
        cur_prop_id = node.propId
        while cur_prop_id != 0:
            prop = self.property_manager.get_item_at_index(cur_prop_id)
            cur_prop_id = prop.nextPropId
            self.delete_property(prop)

        # Delete node itself
        self.node_manager.delete_item(node)

        # Because delete_relation is unaware of whether it's being deleted
        # because a node was deleted, if this node has only ONE relation
        # attached to it, it will be modified during the update_relation_links
        # process. However, the cache thinks the node has been deleted before
        # the write-through process is done, so the node never actually gets
        # removed from the cache
        #
        # TODO: Handle this more gracefully
        if isOnlyRel:
            del self.nodeprop[node.index]

# --- Update Interface Methods --- #
    def update_nodes(self, nodeprops, updates):
        """
        Updates the properties of the given nodes

        :param nodeprops: Nodeprop iterator to get nodes and properties from
        :type nodeprops: NodeIterator
        :param updates: Dict. containing property names and their update values
        :type updates: dict
        :return: Nothing
        :rtype: None
        """
        self.update_properties(nodeprops, updates, True)

    def update_relations(self, relprops, updates):
        """
        Updates the properties of the given relationships

        :param relprops: Nodeprop iterator to get nodes and properties from
        :type relprops: RelationshipIterator
        :param updates: Dict. containing property names and their update values
        :type updates: dict
        :return: Nothing
        :rtype: None
        """
        self.update_properties(relprops, updates, False)

# --- Update Methods --- #
    def update_properties(self, itemprops, updates, node_flag):
        """
        Updates the given nodes or relationship properties
        :param itemprops: nodeprops or relprops to update
        :type itemprops: list[NodeProperty] | list[RelationProperty]
        :param updates: Dict. containing property names and their update values
        :type updates: dict[str, Any]
        :param node_flag: Flag specifying whether we are getting data for
                  a node type (True) or a relationship type (False)
        :type node_flag: bool
        :return: Nothing
        :rtype: None
        """
        if node_flag:
            cache = self.nodeprop
        else:
            cache = self.relprop

        # Sync cache before updates
        cache.sync()

        for itemprop in itemprops:
            if node_flag:
                _, properties = cache[itemprop.node.index]
            else:
                _, properties = cache[itemprop.rel.index]
            # For every update to the properties of the current item
            for index, new_val in updates.iteritems():
                # Property to update
                prop = properties[index]
                # Old value (index of name or array, won't be changed)
                old_val = prop.propBlockId
                # -- Update property value -- #
                # String, so update name
                if prop.is_string():
                    self.prop_string_manager.\
                        update_string_at_index(old_val, new_val)
                # Array, so use array manager
                elif prop.is_array():
                    self.array_manager.\
                        update_array_at_index(old_val, new_val)
                # Otherwise primitive
                else:
                    prop.propBlockId = new_val
                    self.property_manager.write_item(prop)
        # Done with updates, clear cache
        cache.clear()

# --- Alter Methods --- #
    def drop_property(self, type_name, prop_name, node_flag):
        type_data, type_schema = self.get_type_data(type_name, node_flag)

        # Get the appropriate managers
        # Deleting a node property
        if node_flag:
            cache = self.nodeprop
            type_manager = self.nodeTypeManager
            tt_manager = self.nodeTypeTypeManager
            tt_name_manager = self.nodeTypeTypeNameManager
            get_items = self.get_nodes_of_type
        # Deleting a relationship property
        else:
            cache = self.relprop
            type_manager = self.relTypeManager
            tt_manager = self.relTypeTypeManager
            tt_name_manager = self.relTypeTypeNameManager
            get_items = self.get_relations_of_type

        # Here we iterate over the schema of the node/relation to remove the
        # corresponding property
        prev_tt_id = None # schemas are singly-linked, so we need to track this
        cur_tt_id = type_data.firstType
        tt_index = 0
        while cur_tt_id != 0:
            tt = tt_manager.get_item_at_index(cur_tt_id)
            type_name = tt_name_manager.read_string_at_index(tt.typeName)

            if type_name == prop_name:
                next_tt_id = tt.nextType
                if prev_tt_id is not None:
                    # not the first type
                    prev_tt = tt_manager.get_item_at_index(prev_tt_id)
                    prev_tt.nextType = next_tt_id
                    tt_manager.write_item(prev_tt)
                else:
                    # the first type
                    type_data.firstType = next_tt_id
                    type_manager.write_item(type_data)
                self.delete_type_type(tt, node_flag)
                break

            prev_tt_id = cur_tt_id
            cur_tt_id = tt.nextType
            tt_index += 1
        else:
            # If we never broke, that means we never found the desired property.
            raise NonexistentPropertyException("Property with name %s does not exist." % prop_name)

        for item_prop in get_items(type_data):
            if node_flag:
                item = item_prop.node
            else:
                item = item_prop.rel

            # Now we remove the property from every node of this type.
            cur_prop_id = item.propId
            prop_ids = []
            cur_prop_idx = 0
            while cur_prop_id != 0:
                prop = self.property_manager.get_item_at_index(cur_prop_id)

                cur_prop_id = prop.nextPropId

                # The properties are linked in the same order as the schema, so
                # we just need the index.
                if cur_prop_idx == tt_index:
                    # Properties are doubly-linked, so we don't need to keep
                    # track of prev/next.
                    if prop.prevPropId != 0:
                        # Not the first property
                        prev_prop = self.property_manager.get_item_at_index(prop.prevPropId)
                        prev_prop.nextPropId = prop.nextPropId
                        self.property_manager.write_item(prev_prop)
                    else:
                        # The first property
                        item.propId = prop.nextPropId

                    if prop.nextPropId != 0:
                        # Not the last property
                        next_prop = self.property_manager.get_item_at_index(prop.nextPropId)
                        next_prop.prevPropId = prop.prevPropId
                        self.property_manager.write_item(next_prop)
                    # Actually delete it
                    self.delete_property(prop)
                else:
                    # Otherwise, add it to the property list we'll need to
                    # update the cache with. We use ids here rather than the
                    # actual properties because we need to ensure we have the
                    # updated value.
                    prop_ids.append(prop.index)

                cur_prop_idx += 1

            # Update the cache to reflect the new properties
            props = map(self.property_manager.get_item_at_index, prop_ids)
            cache[item.index] = (item, props)
        # Sync cache to disk
        cache.sync()

    def add_property(self, type_name, tt_name, tt_type, node_flag):
        type_data, type_schema = self.get_type_data(type_name, node_flag)

        # Get the appropriate managers
        # Deleting a node property
        if node_flag:
            cache = self.nodeprop
            type_manager = self.nodeTypeManager
            tt_manager = self.nodeTypeTypeManager
            tt_name_manager = self.nodeTypeTypeNameManager
            get_items = self.get_nodes_of_type
        # Deleting a relationship property
        else:
            cache = self.relprop
            type_manager = self.relTypeManager
            tt_manager = self.relTypeTypeManager
            tt_name_manager = self.relTypeTypeNameManager
            get_items = self.get_relations_of_type

        tt_id = tt_manager.get_indexes()[0]
        if tt_type.find("[]") > -1:
            tt_type = tt_type.replace("[]", "Array")
        tt_name_id = tt_name_manager.write_string(tt_name)
        kwargs = {
            "property_type": Property.PropertyType[tt_type],
            "type_name": tt_name_id,
            "index": tt_id
        }
        new_tt = tt_manager.create_item(**kwargs)
        if len(type_schema) > 0:
            last_tt, _, __ = type_schema[-1]
            last_tt.nextType = new_tt.index
            tt_manager.write_item(last_tt)

        default_val = getattr(Property.DefaultValue, tt_type)
        for item_prop in get_items(type_data):
            if node_flag:
                item = item_prop.node
            else:
                item = item_prop.rel
            props = []

            cur_prop_id = item.propId
            last_prop_id = 0
            i = 0
            while cur_prop_id != 0:
                cur_prop = self.property_manager.get_item_at_index(cur_prop_id)
                props.append(cur_prop)
                last_prop_id = cur_prop_id
                cur_prop_id = cur_prop.nextPropId

            index = self.property_manager.get_indexes()[0]
            kwargs = self.generate_property_args(index, Property.PropertyType[tt_type], default_val)
            stored_prop = self.property_manager.create_item(**kwargs)

            if last_prop_id == 0:
                # If this is 0, that means we were in a relation with an empty
                # schema.
                item.propId = stored_prop.index
            else:
                # Otherwise, there was a schema beforehand.
                stored_prop.prevPropId = last_prop_id
                props[-1].nextPropId = stored_prop.index
                self.property_manager.write_item(props[-1])

            props.append(stored_prop)
            cache[item.index] = (item, props)
        # Sync cache to disk
        cache.sync()

        return new_tt

    def change_property(self, type_name, tt_name, new_tt_type, node_flag):
        type_data, type_schema = self.get_type_data(type_name, node_flag)

        # Get the appropriate managers
        # Changing a node property
        if node_flag:
            cache = self.nodeprop
            type_manager = self.nodeTypeManager
            tt_manager = self.nodeTypeTypeManager
            tt_name_manager = self.nodeTypeTypeNameManager
            get_items = self.get_nodes_of_type
        # Changing a relationship property
        else:
            cache = self.relprop
            type_manager = self.relTypeManager
            tt_manager = self.relTypeTypeManager
            tt_name_manager = self.relTypeTypeNameManager
            get_items = self.get_relations_of_type

        for i, (tt, name, tt_type) in enumerate(type_schema):
            if name == tt_name:
                prop_index = i
                prop = tt
                prop_type = tt_type
                break
        else:
            raise NonexistentPropertyException("Property with name %s does not exist." % tt_name)

        if new_tt_type.find("[]") > -1:
            new_tt_type = new_tt_type.replace("[]", "Array")
        new_type = Property.PropertyType[new_tt_type]
        old_type = prop.propertyType
        prop.propertyType = new_type

        tt_manager.write_item(prop)

        for item_prop in get_items(type_data):
            if node_flag:
                item = item_prop.node
            else:
                item = item_prop.rel
            props = []
            old_value = item_prop.properties[prop_index]
            new_value = self.convert_value_between_types(old_value, old_type, new_type)

            cur_prop_id = item.propId
            i = 0
            while cur_prop_id != 0:
                cur_prop = self.property_manager.get_item_at_index(cur_prop_id)
                if i == prop_index:
                    cur_prop.type = new_type
                    if Property.PropertyType.is_array(new_type):
                        if Property.PropertyType.is_array(old_type):
                            # Already had an array, so update
                            array_idx = cur_prop.propBlockId
                            array_block = self.array_manager.storeManager.get_item_at_index(array_idx)
                            array_block.type = new_type
                            self.array_manager.storeManager.write_item(array_block)
                            self.array_manager.update_array_at_index(cur_prop.propBlockId, new_value)
                        else:
                            # Didn't have an array before, so have to write an
                            # array and put it there
                            cur_prop.propBlockId = self.array_manager.write_array(new_value, new_type)
                    elif Property.PropertyType.is_string(new_type):
                        if Property.PropertyType.is_string(old_type):
                            # Already had a string, so update
                            self.prop_string_manager.update_string_at_index(cur_prop.propBlockId, new_value)
                        else:
                            cur_prop.propBlockId = self.prop_string_manager.write_string(new_value)
                    else:
                        cur_prop.propBlockId = new_value
                props.append(cur_prop)
                cur_prop_id = cur_prop.nextPropId
                i += 1

            cache[item.index] = (item, props)
        # Sync cache to disk
        cache.sync()

    def rename_property(self, type_name, tt_name, new_tt_name, node_flag):
        type_data, type_schema = self.get_type_data(type_name, node_flag)

        # Get the appropriate managers
        # Renaming a node property
        if node_flag:
            cache = self.nodeprop
            type_manager = self.nodeTypeManager
            tt_manager = self.nodeTypeTypeManager
            tt_name_manager = self.nodeTypeTypeNameManager
        # Renaming a relationship property
        else:
            cache = self.relprop
            type_manager = self.relTypeManager
            tt_manager = self.relTypeTypeManager
            tt_name_manager = self.relTypeTypeNameManager

        # Here we iterate over the schema of the node/relation to rename the
        # corresponding property
        cur_tt_id = type_data.firstType
        tt_index = 0
        while cur_tt_id != 0:
            tt = tt_manager.get_item_at_index(cur_tt_id)
            type_name = tt_name_manager.read_string_at_index(tt.typeName)

            if type_name == tt_name:
                name_id = tt.typeName
                tt_name_manager.update_string_at_index(name_id, new_tt_name)
                break

            cur_tt_id = tt.nextType
            tt_index += 1
        else:
            # If we never broke, that means we never found the desired property.
            raise NonexistentPropertyException("Property with name %s does not exist." % tt_name)


# --- Helpers --- #
    def generate_property_args(self, index, prop_type, prop_val):
        kwargs = {
            "index": index,
            "prop_type": prop_type
        }

        # String, so write name
        if prop_type == Property.PropertyType.string:
            kwargs["prop_block_id"] = \
                self.prop_string_manager.write_string(prop_val)
        # Array, so use array manager
        elif prop_type.value >= Property.PropertyType.intArray.value:
            kwargs["prop_block_id"] = \
                self.array_manager.write_array(prop_val, prop_type)
        # Otherwise primitive
        else:
            kwargs["prop_block_id"] = prop_val

        return kwargs

    def is_convertible(self, from_type, to_type):
        # Obviously, a type can be converted to itself.
        if from_type == to_type:
            return True
        elif Property.PropertyType.is_array(from_type):
            # T[] to S[] is valid only if T to S is.
            if Property.PropertyType.is_array(to_type):
                return self.is_convertible(Property.PropertyType.get_base_type(from_type),
                                           Property.PropertyType.get_base_type(to_type))
            # T[] to S is not valid.
            else:
                return False
        elif Property.PropertyType.is_array(to_type):
            # T to S[] is valid only if T to S is valid.
            return self.is_convertible(from_type, Property.PropertyType.get_base_type(to_type))
        else:
            # T to S case, so we actually have to check.
            if to_type == Property.PropertyType.bool or \
               to_type == Property.PropertyType.char:
                # Can't convert to a bool from anything other than a bool, same
                # with chars
                return False
            elif from_type == Property.PropertyType.char and \
                 to_type == Property.PropertyType.string:
                # chars are convertible to strings
                return True
            elif (from_type == Property.PropertyType.bool or \
                  Property.PropertyType.is_numerical(from_type)) and \
                 Property.PropertyType.is_numerical(to_type):
                # bools are convertible to numbers (True -> 1, False -> 0), and
                # number to number is fine.
                return True
        return False

    def convert_value_between_types(self, value, from_type, to_type):
        """
        Converts a value from one type to the other. There are a few potential
        caveats here.

        Converting from type T[] to type S will always result in the default
        value for S, as there is no obvious choice for how to convert an array
        to a single value.

        Converting from type T to type S will attempt to convert from T to S if
        the values have valid conversion methods; otherwise, we will return the
        default value for S.

        Converting from type T to type T[] will result in the original value
        being wrapped in an array; e.g. from int to int[], 3 will be converted
        into [3].

        Converting from type T to type S[] has two possibilities. If T can be
        converted validly to S, then that value is converted first and then
        wrapped in an array. If not, we return the default value for S[].

        Converting from T[] to type S[] works similarly as T to S[]; if T is
        convertible to S, then we convert each value in the array. Otherwise, we
        return the default value of S[].

        :param value: Original value of property
        :type value: object
        :param from_type: Original type
        :type from_type: Property.PropertyType
        :param to_type: New type
        :type to_type: Property.PropertyType
        :return: The converted value
        :rtype: object
        """
        if not self.is_convertible(from_type, to_type):
            return getattr(Property.DefaultValue, to_type.name)
        elif from_type == to_type:
            return value
        else:
            if Property.PropertyType.is_array(to_type):
                # Converting to an array...
                if Property.PropertyType.is_array(from_type):
                    # If the original is an array, do a map
                    from_base = Property.PropertyType.get_base_type(from_type)
                    to_base = Property.PropertyType.get_base_type(to_type)
                    return map(lambda v: self.convert_value_between_types(v, from_base, to_base),
                               value)
                else:
                    # Otherwise, just wrap value
                    return [value]
            elif from_type == Property.PropertyType.bool:
                # Bool can only be converted to a number, so make a number first
                # then convert.
                num_value = 1 if value else 0
                return self.convert_value_between_types(num_value, Property.PropertyType.int, to_type)
            elif from_type == Property.PropertyType.char:
                # Chars can be converted to strings... doesn't actually change
                # the value though
                return value
            else:
                # Otherwise dealing with numerical conversions.
                if to_type in [Property.PropertyType.float, Property.PropertyType.double]:
                    # Float/Double
                    return float(value)
                else:
                    # Integer of some kind
                    return int(value)

# --- Tools --- #
    def cache_diagnostic(self):
        """
        Print out diagnostic information about the pylru cache

        :return: Nothing
        :rtype: None
        """
        self.logger.debug("Node cache size: %d" % len(self.nodeprop.cache))
        self.logger.debug("Relationship cache size: %d" % len(self.relprop.cache))
