

class DefragManager():
    def __init__(self, storage_manager):
        self.storageManager = storage_manager

    def defragment(self, store_manager):
        """
        Defragments the given store manager and updates any references

        :param store_manager: Store manager to defragment
        :type store_manager: GeneralStoreManager
        :return:
        :rtype:
        """
        base_store = store_manager.store
        id_store = store_manager.idStore

    def get_referencing_store(self, base_store):

