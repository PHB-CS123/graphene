from graphene.commands.command import Command

class DeleteRelationCommand(Command):
    def __init__(self, data):
        self.rel_name = data.t

    def execute(self, storage_manager):
        storage_manager.delete_relationship_type(self.rel_name)
