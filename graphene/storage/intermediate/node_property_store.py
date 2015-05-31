from graphene.storage import GeneralStore, Node, Property
from graphene.storage.intermediate import GeneralNameManager
from graphene.storage.intermediate.node_property import NodeProperty

class NodePropertyStore:
    def __init__(self, storage_manager):
        """
        Set up the node-property store, which associates
        nodes with their properties.

        :param storage_manager: Store manager containing needed stores
        :type storage_manager: StoreManager
        :return: Store for handling nodes and properties
        :rtype: NodePropertyStore
        """
        self.sm = storage_manager
        self.node_manager = self.sm.node_manager
        self.prop_manager = self.sm.property_manager

    def __getitem__(self, key):
        """
        Get the node and an array of the properties for the node

        :param key: Index of the node
        :type key: int
        :return: Tuple with node and property array
        :rtype: tuple
        """
        cur_node = self.node_manager.get_item_at_index(key)
        if cur_node is None or cur_node == GeneralStore.EOF:
            return cur_node
        properties = []
        cur_prop_id = cur_node.propId
        while cur_prop_id != 0:
            cur_prop = self.prop_manager.get_item_at_index(cur_prop_id)
            properties.append(cur_prop)
            cur_prop_id = cur_prop.nextPropId
        return cur_node, properties

    def __setitem__(self, key, value):
        if isinstance(value[0], Node) and \
           all(isinstance(p, Property) for p in value[1]):
            node, properties = value
            self.node_manager.write_item(node)
            for prop in properties:
                self.prop_manager.write_item(prop)
        else:
            raise ValueError("Given value is not a Node instance")

    def __delitem__(self, key):
        node = self.node_manager.get_item_at_index(key)
        if node is None:
            raise KeyError("There is no node with index %d." % key)
        if node == GeneralStore.EOF:
            raise IndexError("Key %d goes past the end of the store." % key)
        self.sm.delete_node(node)