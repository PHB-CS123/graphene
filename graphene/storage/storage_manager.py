from graphene.storage.base.node_store import *
from graphene.storage.base.property_store import *
from graphene.storage.base.relationship_store import *

from graphene.storage.intermediate import *
from pylru import WriteBackCacheManager


class StorageManager:

    MAX_CACHE_SIZE = 100

    def __init__(self):
        self.node_store = NodeStore()
        self.prop_store = PropertyStore()
        self.rel_store = RelationshipStore()

        nodeprop = NodePropertyStore(self.node_store, self.prop_store)
        self.nodeprop = WriteBackCacheManager(nodeprop, self.MAX_CACHE_SIZE)
        # self.relprop = RelationPropertyStore(self.rel_store, self.prop_store)
