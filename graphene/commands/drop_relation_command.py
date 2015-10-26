import sys

from graphene.commands.command import Command

class DropRelationCommand(Command):
    """
    Used to delete relation types from the database.
    """
    def __init__(self, data):
        self.rel_name = data.t

    def execute(self, storage_manager, output=sys.stdout, timer=None):
        storage_manager.delete_relationship_type(self.rel_name)
