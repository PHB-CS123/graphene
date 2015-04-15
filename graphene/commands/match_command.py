from graphene.commands.command import Command

class MatchCommand(Command):
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        lst = ["\t%s" % chain for chain in self.data]
        return "[Match\n%s\n]" % "\n".join(lst)

    def execute(self, storage_manager):
        i = 1
        while True:
            node = storage_manager.nodeprop[i]
            if node is None:
                break
            print node
            i += 1
