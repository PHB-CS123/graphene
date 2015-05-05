import sys

from graphene.traversal import *
from graphene.commands.command import Command
from graphene.utils import PrettyPrinter
from graphene.query.planner import QueryPlanner

class MatchCommand(Command):
    def __init__(self, node_chain, query_chain, return_chain):
        self.nc = node_chain
        self.qc = query_chain or ()
        self.rc = return_chain or ()

    def __repr__(self):
        lst = ["\t%s" % chain for chain in self.nc]
        return "[Match\n%s\n]" % "\n".join(lst)

    def execute(self, storage_manager, output=sys.stdout):
        # Create a planner and execute given a node chain and query chain
        planner = QueryPlanner(storage_manager)
        schema, results = planner.execute(self.nc, self.qc, self.rc)

        # If there's nothing found, there were no nodes
        if len(results) == 0:
            output.write("No nodes found.\n")
            return []

        PrettyPrinter.print_table(results, schema, output)
        return results
