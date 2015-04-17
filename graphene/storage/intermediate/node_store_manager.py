from graphene.storage.id_store import *
from graphene.storage.node_store import *


class NodeStoreManager:
    """
    Handles the creation/deletion of nodes to the NodeStore with ID recycling
    """

    def __init__(self, store):

        self.store = store
        self.idStore = IdStore(store.FILE_NAME + ".id")

    def create_item(self):

        available_id = self.idStore.get_id()

