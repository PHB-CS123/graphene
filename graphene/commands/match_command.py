import sys

from graphene.traversal import *
from graphene.commands.command import Command
from graphene.utils import PrettyPrinter

class MatchCommand(Command):
    def __init__(self, node_chain, query_chain):
        self.nc = node_chain
        self.qc = query_chain or ()

    def __repr__(self):
        lst = ["\t%s" % chain for chain in self.nc]
        return "[Match\n%s\n]" % "\n".join(lst)

    def execute(self, storage_manager, output=sys.stdout):
        # TODO: handle relationships, passes a True argument for node flag
        first_match = self.nc[0]
        alias = first_match.name
        type_data, type_schema = storage_manager.get_node_data(first_match.type)
        qc = Query.parse_chain(storage_manager, self.qc, type_schema, alias)

        header = [name.upper() for tt, name, ttype in type_schema]
        iterator = NodeIterator(storage_manager, type_data, type_schema, alias, qc)
        values = []
        for node in iterator:
            values.append(node.properties)
        if len(values) == 0:
            output.write("No nodes found.\n")
            return []
        PrettyPrinter.print_table(values, header, output)
        return values
