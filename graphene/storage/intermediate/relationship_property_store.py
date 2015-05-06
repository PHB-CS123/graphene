from graphene.storage import GeneralStore, Relationship, Property
from graphene.storage.intermediate import GeneralStoreManager

class RelationshipPropertyStore:
    def __init__(self, relationship_manager, prop_manager):
        """
        Set up the relationship-property store, which associates
        relationships with their properties.

        :type prop_manager: GeneralStoreManager
        :type relationship_manager: GeneralStoreManager
        :param relationship_manager: store manager for relationships
        :param prop_manager: store manager for properties
        :return:
        """
        self.relationship_manager = relationship_manager
        self.prop_manager = prop_manager

    def __getitem__(self, key):
        cur_relationship = self.relationship_manager.get_item_at_index(key)
        if cur_relationship is None or cur_relationship == GeneralStore.EOF:
            return cur_relationship
        properties = []
        cur_prop_id = cur_relationship.propId
        while cur_prop_id != 0:
            cur_prop = self.prop_manager.get_item_at_index(cur_prop_id)
            properties.append(cur_prop)
            cur_prop_id = cur_prop.nextPropId
        return (cur_relationship, properties)

    def __setitem__(self, key, value):
        if isinstance(value[0], Relationship) and \
           all(isinstance(p, Property) for p in value[1]):
            rel, properties = value
            self.relationship_manager.write_item(rel)
            for prop in properties:
                self.prop_manager.write_item(prop)
        else:
            # TODO: Throw an error here
            pass

    def __delitem__(self, key):
        rel = self.relationship_manager.get_item_at_index(key)
        if rel is None:
            raise KeyError("There is no relationship with index %d." % key)
        if rel == GeneralStore.EOF:
            raise IndexError("Key %d goes past the end of the store." % key)
        cur_prop_id = rel.propId
        while cur_prop_id != 0:
            cur_prop = self.prop_manager.get_item_at_index(cur_prop_id)
            cur_prop_id = cur_prop.nextPropId
            self.prop_manager.delete_item(cur_prop)
        self.relationship_manager.delete_item(rel)
