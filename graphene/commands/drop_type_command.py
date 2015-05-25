from graphene.commands.command import Command

class DropTypeCommand(Command):
    def __init__(self, data):
        self.type_name = data.t

    def execute(self, storage_manager):
        storage_manager.delete_node_type(self.type_name)
