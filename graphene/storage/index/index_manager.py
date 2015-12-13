import atexit
import os

from graphene.storage.index.index_store import IndexStore


class IndexManager(object):
    """
    :type nodeIndexes: dict[int, IndexStore]
    :type relationshipIndexes: dict[int, IndexStore]
    """
    INDEXES_SUBFOLDER = "indexes/"
    INDEX_FILE_EXTENSION = ".idx"
    # Singleton class variable
    GLOBAL_INDEX_MANAGER = None

    def __new__(cls, *args, **kwargs):
        assert IndexManager.GLOBAL_INDEX_MANAGER is None, \
            "IndexManager should be a singleton"
        IndexManager.GLOBAL_INDEX_MANAGER = object.__new__(cls)
        return IndexManager.GLOBAL_INDEX_MANAGER

    def __init__(self):
        from graphene.storage.base.graphene_store import GrapheneStore
        self.indexesDir = GrapheneStore().datafilesDir + self.INDEXES_SUBFOLDER
        # Create indexes sub-directory if it does not exist
        if not os.path.exists(self.indexesDir):
            os.mkdir(self.indexesDir)
        # Dictionaries of loaded indexes
        self.nodeIndexes = {}
        self.relationshipIndexes = {}
        self.GLOBAL_INDEX_MANAGER = self

    def flush_indexes(self):
        map(lambda x: x.write_index_set_to_file(),
            self.nodeIndexes.values() + self.relationshipIndexes.values())

    def get_indexes_for_node_type(self, node_type):
        """
        Returns a set of indexes of nodes with the given node type

        :param node_type: Index of the node type
        :type node_type: int
        :return: Set of indexes for the given node type index
        :rtype: set(int)
        """
        self._load_index_for_type(node_type, is_node=True)
        return self.nodeIndexes[node_type].get_index_set()

    def get_indexes_for_rel_type(self, rel_type):
        """
        Returns a set of indexes of relationships with the given rel type

        :param rel_type: Index of the relationship type
        :type rel_type: int
        :return: Set of indexes for the given node type index
        :rtype: set(int)
        """
        self._load_index_for_type(rel_type, is_node=False)
        return self.relationshipIndexes[rel_type].get_index_set()

    def handle_node_insert(self, node_type, node, properties):
        """
        Handle the insertion of the node into the database

        :param node_type: Index of the node type
        :type node_type: int
        :param node: Index of the node
        :type node: int
        :param properties: Indexes of the inserted properties for the node
        :type properties: list[int]
        :return: Nothing
        :rtype: None
        """
        self._handle(node_type, node, properties, is_node=True, is_insert=True)

    def handle_node_delete(self, node_type, node, properties):
        """
        Handle the deletion of the node from the database

        :param node_type: Index of the node type
        :type node_type: int
        :param node: Index of the node
        :type node: int
        :param properties: Indexes of the deleted properties for the node
        :type properties: list[int]
        :return: Nothing
        :rtype: None
        """
        self._handle(node_type, node, properties, is_node=True, is_insert=False)

    def handle_rel_insert(self, rel_type, rel, properties):
        """
        Handle the insertion of the relationship into the database

        :param rel_type: Index of the relationship type
        :type rel_type: int
        :param rel: Index of the relationship
        :type rel: int
        :param properties: Indexes of the inserted properties for the rel
        :type properties: list[int]
        :return: Nothing
        :rtype: None
        """
        self._handle(rel_type, rel, properties, is_node=False, is_insert=True)

    def handle_rel_delete(self, rel_type, rel, properties):
        """
        Handle the deletion of the relationship from the database

        :param rel_type: Index of the node type
        :type rel_type: int
        :param rel: Index of the node
        :type rel: int
        :param properties: Indexes of the deleted properties for the rel
        :type properties: list[int]
        :return: Nothing
        :rtype: None
        """
        self._handle(rel_type, rel, properties, is_node=False, is_insert=False)

    def delete_index_for_node_type(self, node_type):
        """
        Delete the index for the given node type

        :param node_type: Index of the node type to delete the index of
        :type node_type: int
        :return: Nothing
        :rtype: None
        """
        self._load_index_for_type(node_type, False)
        self.relationshipIndexes[node_type].delete_index()

    def delete_index_for_rel_type(self, rel_type):
        """
        Delete the index for the given relationship type

        :param rel_type: Index of the relationship type to delete the index of
        :type rel_type: int
        :return: Nothing
        :rtype: None
        """
        self._load_index_for_type(rel_type, False)
        self.relationshipIndexes[rel_type].delete_index()

    def _handle(self, item_type, item, properties, is_node, is_insert):
        """
        Handle the insertion of the node or relationship into the database

        :param item_type: Index of the item type
        :type item_type: int
        :param item: Index of the item
        :type item: int
        :param properties: Indexes of the inserted properties for the node
        :type properties: list[int]
        :param is_node: True if this is for a node insert, False for rel insert
        :type is_node: bool
        :param is_insert: True if this is an insert, False if it is a delete
        :type is_insert: bool
        :return: Nothing
        :rtype: None
        """
        # TODO: handle properties with B-tree implementation
        indexes = self.nodeIndexes if is_node else self.relationshipIndexes
        # Load and get the appropriate index
        self._load_index_for_type(item_type, is_node)
        index_store = indexes[item_type]
        # Insert or delete accordingly
        if is_insert:
            index_store.handle_insert(item)
        else:
            index_store.handle_delete(item)

    def _delete_index_for_type(self, item_type, is_node):
        """
        Deletes the index for the given item type

        :param item_type: Index of the type
        :type item_type: int
        :param is_node: True if this is for a node insert, False for rel insert
        :type is_node: bool
        :return: Nothing
        :rtype: None
        """
        indexes = self.nodeIndexes if is_node else self.relationshipIndexes
        # Load and get the appropriate index
        self._load_index_for_type(item_type, is_node)
        index_store = indexes[item_type]
        index_store.delete_index()
        del indexes[item_type]

    def _load_index_for_type(self, item_type, is_node):
        indexes = self.nodeIndexes if is_node else self.relationshipIndexes
        # Open the index if not already opened
        if item_type not in indexes:
            index_store = IndexStore(self.filename_for_type(item_type, is_node))
            indexes[item_type] = index_store

    def filename_for_type(self, type_idx, is_node):
        index_filename = "N" + str(type_idx) if is_node else "R" + str(type_idx)
        return self.indexesDir + index_filename + self.INDEX_FILE_EXTENSION


@atexit.register
def exit_handler():
    if IndexManager.GLOBAL_INDEX_MANAGER:
        IndexManager.GLOBAL_INDEX_MANAGER.flush_indexes()