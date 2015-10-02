import sys

from graphene.traversal import *
from graphene.commands.command import Command
from graphene.utils import PrettyPrinter, CmdTimer
from graphene.query.planner import QueryPlanner

class MatchCommand(Command):
    def __init__(self, node_chain, query_chain, return_chain, limit):
        self.nc = node_chain
        self.qc = query_chain
        self.rc = return_chain or ()
        self.limit = limit or 0
        if self.limit < 0:
            self.limit = 0

    def __repr__(self):
        lst = ["\t%s" % chain for chain in self.nc]
        return "[Match\n%s\n]" % "\n".join(lst)

    def execute(self, storage_manager, output=sys.stdout, timer=CmdTimer()):
        """
        Runs a MATCH query against the server

        :type storage_manager: StorageManager
        :param storage_manager: storage manager for this instance
        :type output: file
        :param output: The file stream to pipe output into
        :return: List of results
        """
        # Instance of pretty printer to use for all output
        printer = PrettyPrinter()

        # Create a planner and execute given a node chain and query chain
        planner = QueryPlanner(storage_manager)
        schema, results = planner.execute(self.nc, self.qc, self.rc, limit=self.limit)

        with timer.paused():
            # If there's nothing found, there were no nodes
            if len(results) == 0:
                printer.print_info("No results found.\n", output)
                return []

            printer.print_table(results, schema, output)
            printer.print_info("%d result(s) found.\n" % len(results))
        return results
