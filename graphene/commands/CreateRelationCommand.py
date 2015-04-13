from graphene.commands.Command import Command

class CreateRelationCommand(Command):
    def __init__(self, ctx):
        self.rel_name = ctx.r;
        self.first_type = ctx.t1;
        self.second_type = ctx.t2;

    def __repr__(self):
        fmt = """[Create (Relation)
    Name: %s
    Mapping: %s -> %s
]"""
        return fmt % (self.rel_name, self.first_type, self.second_type)
