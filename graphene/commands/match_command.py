import sys

from graphene.commands.command import Command
from graphene.utils import PrettyPrinter

class MatchCommand(Command):
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        lst = ["\t%s" % chain for chain in self.data]
        return "[Match\n%s\n]" % "\n".join(lst)

    def execute(self, storage_manager):
        # We only handle the first match for now...
        first_match = self.data[0]
        type_data, type_schema = storage_manager.get_type_data(first_match.type)
        header = [name.upper() for tt, name, ttype in type_schema]
        i = 1
        values = []
        while True:
            node = storage_manager.get_node(i)
            if node is None:
                break
            i += 1
            if node.type != type_data:
                continue
            values.append(node.properties)
        if len(values) == 0:
            sys.stdout.write("No nodes found.\n")
            return
        PrettyPrinter.print_table(values, header)
