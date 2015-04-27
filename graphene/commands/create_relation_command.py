from graphene.commands.command import Command

class CreateRelationCommand(Command):
    def __init__(self, ctx):
        self.rel_name = ctx.r
        self.type_list = ctx.tl or ()

    def execute(self, storage_manager):
        print self.rel_name, self.type_list
