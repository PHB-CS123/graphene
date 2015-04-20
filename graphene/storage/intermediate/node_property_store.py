class NodePropertyStore:
    def __init__(self, node_manager, prop_manager):
        self.node_manager = node_manager
        self.prop_manager = prop_manager

    def __getitem__(self, key):
        cur_node = self.node_manager.get_item_at_index(key)
        if cur_node is None:
            return None
        properties = []
        cur_prop = self.prop_manager.get_item_at_index(cur_node.propId)
        while cur_prop is not None:
            properties.append(cur_prop)
            cur_prop = self.prop_store.item_at_index(cur_prop.nextPropId)
        return cur_node, properties

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass
