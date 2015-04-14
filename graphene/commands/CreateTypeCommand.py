from graphene.commands.Command import Command

class CreateTypeCommand(Command):
    def __init__(self, ctx):
        self.type_name = ctx.t
        self.type_list = ctx.tl

    def __repr__(self):
        fmt = """[Create (Type)
    Name = %s
    Schema = (
%s
    )
]"""
        return fmt % (self.type_name,
                        ",\n".join("\t%s %s" % decl for decl in self.type_list))
