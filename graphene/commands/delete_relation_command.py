from graphene.commands.relation_iterator import *

class DeleteRelationCommand(RelationIterator):
    """
    Used to delete individual relations from the database.
    """
    def __init__(self, rel_type, query_chain, left_node, right_node):
        super(DeleteRelationCommand, self).__init__(rel_type, query_chain,
                                                    left_node, right_node)

    def execute(self, storage_manager):
        """
        Deletes the relationships obtained from the relation iterator

        :param storage_manager: Storage manager to get data from
        :type storage_manager: StorageManager
        :return: Nothing
        :rtype: None
        """
        # Get relation iterator
        rel_iter = super(DeleteRelationCommand, self).execute(storage_manager)
        # Delete relations yielded by generator
        for rel in rel_iter:
            del storage_manager.relprop[rel.index]
