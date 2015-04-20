class RelationshipPropertyStore:
    def __init__(self, relationship_manager, prop_manager):
        self.relationship_manager = relationship_manager
        self.prop_manager = prop_manager

    def __getitem__(self, key):
        cur_relationship = self.relationship_manager.get_item_at_index(key)
        if cur_relationship is None:
            return None
        properties = []
        cur_prop = self.prop_manager.get_item_at_index(cur_relationship.propId)
        while cur_prop is not None:
            properties.append(cur_prop)
            cur_prop = self.prop_manager.get_item_at_index(cur_prop.nextPropId)
        return (cur_relationship, properties)

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass
