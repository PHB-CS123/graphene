from graphene.storage import StorageManager
from graphene.commands.command import Command


class CreateRelationCommand(Command):
    def __init__(self, ctx):
        self.rel_name = ctx.r
        self.type_list = ctx.tl or ()

    def execute(self, storage_manager, timer=None):
        """
        Create the relation specified by this class.
        :type storage_manager: StorageManager
        :param storage_manager: manager that stores the relation to disk
        :return: None
        """
        storage_manager.create_relationship_type(self.rel_name, self.type_list)
