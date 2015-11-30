import sys

from graphene.commands.command import Command


class CreateTypeCommand(Command):
    def __init__(self, ctx):
        self.type_name = ctx.t
        self.type_list = ctx.tl

    def __repr__(self):
        fmt = """[Create (Type) Name = %s Schema = (\n%s\n)\n]"""
        return fmt % (self.type_name,
                      ",\n".join("\t%s %s" % decl for decl in self.type_list))

    def execute(self, storage_manager, output=sys.stdout, timer=None):
        created_type = storage_manager.create_node_type(self.type_name,
                                                        self.type_list)
