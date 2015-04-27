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
        # We only handle the first match for now...
        first_match = self.nc[0]
        qc = []
        type_data, type_schema = storage_manager.get_type_data(first_match.type)

        for q in self.qc:
            if type(q) == tuple:
                # actual query
                name, oper, value = q
                tt = filter(lambda t: t[1] == name, type_schema)
                if len(tt) == 0:
                    # no such named property
                    raise Exception("%s is not a valid property name." % name)
                ttype = tt[0][2]
                qc.append(Query(name, oper, storage_manager.convert_to_value(value, ttype)))
            else:
                qc.append(q)

        header = [name.upper() for tt, name, ttype in type_schema]
        iterator = NodeIterator(storage_manager, type_data, type_schema, qc)
        values = []
        for node in iterator:
            values.append(node.properties)
        if len(values) == 0:
            output.write("No nodes found.\n")
            return []
        PrettyPrinter.print_table(values, header, output)
        return values
