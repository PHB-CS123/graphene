from graphene.storage.defrag.defragmenter import Defragmenter


class DefragManager:

    def __init__(self, storage_manager):
        self.storageManager = storage_manager
        self.reference_map = self.build_reference_map(storage_manager)
        self.name_stores = self.get_name_stores(storage_manager)

    def defragment(self, store_manager):
        """
        Defragments the given store manager and updates any references

        :param store_manager: Store manager to defragment
        :type store_manager: GeneralStoreManager
        :return: Nothing
        :rtype: None
        """
        base_store = store_manager.store
        id_store = store_manager.idStore
        ref_stores = self.reference_map[base_store]
        is_name = store_manager in self.name_stores
        Defragmenter(base_store, id_store, ref_stores, is_name).defragment()

    def full_defragment(self):
        # TODO: this should only need to be run in some store groups
        pass

    @staticmethod
    def build_reference_map(sm):
        """
        Builds all inward references using the given storage manager

        :param sm: Storage manager to build inward references from
        :type sm: StorageManager
        :return: Dict mapping manager instances to instances that refer to them
        :rtype: dict[GeneralStoreManager, list[GeneralStoreManager]]
        """
        # Get all the base stores
        # Key => t: type, tt: type type, n: name, s: string, a: array
        node_base = sm.node_manager.store
        node_t_base = sm.nodeTypeManager.store
        node_t_n_base = sm.nodeTypeNameManager.storeManager.store
        node_tt_base = sm.nodeTypeTypeManager.store
        node_tt_n_base = sm.nodeTypeTypeNameManager.storeManager.store

        rel_base = sm.relationship_manager.store
        rel_t_base = sm.relTypeManager.store
        rel_t_n_base = sm.relTypeNameManager.storeManager.store
        rel_tt_base = sm.relTypeTypeManager.store
        rel_tt_n_base = sm.relTypeTypeNameManager.storeManager.store

        prop_base = sm.property_manager.store
        prop_s_base = sm.prop_string_manager.storeManager.store
        prop_a_base = sm.array_manager.storeManager.store
        prop_a_s_base = sm.array_manager.stringStoreManager.storeManager.store

        return {
            # Nodes | Node Types | Node Type Types | Node Type & Type Type Names
            node_base: [rel_base],
            node_t_base: [node_base],
            node_t_n_base: [node_t_base],
            node_tt_base: [node_t_base],
            node_tt_n_base: [node_tt_base],
            # Rels | Rels Types | Rels Type Types | Rels Type & Type Type Names
            rel_base: [node_base],
            rel_t_base: [rel_base],
            rel_t_n_base: [rel_t_base],
            rel_tt_base: [rel_t_base],
            rel_tt_n_base: [rel_tt_base],
            # Properties | Strings | Arrays | String Arrays
            prop_base: [node_base, rel_base],
            prop_s_base: [prop_base],
            prop_a_base: [prop_base],
            prop_a_s_base: [prop_a_base],
        }

    @staticmethod
    def get_name_stores(sm):
        """
        Get a list of all the base stores that handle names

        :param sm: Storage manager to get the name base stores from
        :type sm: StorageManager
        :return: List of base stores that handle names
        :rtype: list[GeneralStoreManager]
        """
        return [sm.nodeTypeNameManager.storeManager.store,
                sm.nodeTypeTypeNameManager.storeManager.store,
                sm.relTypeNameManager.storeManager.store,
                sm.relTypeTypeNameManager.storeManager.store]

    @staticmethod
    def get_all_base_stores(sm):
        # Get all the base stores
        # Key => t: type, tt: type type, n: name, s: string, a: array
        node_base = sm.node_manager.store
        node_t_base = sm.nodeTypeManager.store
        node_t_n_base = sm.nodeTypeNameManager.storeManager.store
        node_tt_base = sm.nodeTypeTypeManager.store
        node_tt_n_base = sm.nodeTypeTypeNameManager.storeManager.store

        rel_base = sm.relationship_manager.store
        rel_t_base = sm.relTypeManager.store
        rel_t_n_base = sm.relTypeNameManager.storeManager.store
        rel_tt_base = sm.relTypeTypeManager.store
        rel_tt_n_base = sm.relTypeTypeNameManager.storeManager.store

        prop_base = sm.property_manager.store
        prop_s_base = sm.prop_string_manager.storeManager.store
        prop_a_base = sm.prop_array_manager.storeManager.store
        prop_a_s_base = sm.prop_array_manager.stringStoreManager.store

        return [node_base, node_t_base, node_t_n_base, node_tt_base,
                node_tt_n_base, rel_base, rel_t_base, rel_t_n_base,
                rel_tt_base, rel_tt_n_base, prop_base, prop_s_base,
                prop_a_base, prop_a_s_base]