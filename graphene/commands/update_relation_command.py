from relation_iterator import *


class UpdateRelationCommand(RelationIterator):
    """
    Used to update individual relations from the database.
    """
    def __init__(self, rel_type, query_chain, left_node, right_node, update):
        # Update dictionary
        self.update = update
        super(UpdateRelationCommand, self).__init__(rel_type, query_chain,
                                                    left_node, right_node)

    def execute(self, storage_manager):
        """
        Update the relationship properties from the query

        :param storage_manager: Storage manager to obtain data from
        :type storage_manager: StorageManager
        :return:
        :rtype:
        """
        # Get relation iterator
        rel_iter = super(UpdateRelationCommand, self).execute(storage_manager)
        # Update relation properties yielded by generator
        storage_manager.update_relations(rel_iter, self.update)
