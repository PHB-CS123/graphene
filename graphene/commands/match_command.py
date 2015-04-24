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
        header = [storage_manager.type_type_name_manager \
                .read_name_at_index(tt.typeName).upper() for tt in type_schema]
        i = 1
        values = []
        while True:
            node = storage_manager.nodeprop[i]
            if node is None:
                break
            i += 1
            file_node, props = node
            if storage_manager.get_node_type(file_node) != type_data:
                continue
            values.append(map(storage_manager.get_property_value, props))
        if len(values) == 0:
            sys.stdout.write("No nodes found.\n")
            return
        PrettyPrinter.print_table(values, header)
