from graphene.commands.command import Command

class DropTypeCommand(Command):
    """
    Used to delete node types from the database.
    """
    def __init__(self, data):
        self.type_name = data.t

    def execute(self, storage_manager, timer=None):
        storage_manager.delete_node_type(self.type_name)
