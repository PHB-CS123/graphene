import sys
from collections import Counter

from graphene.errors import TooManyClausesException
from graphene.expressions import OptionalClause
from graphene.traversal import *
from graphene.commands.command import Command
from graphene.utils import PrettyPrinter
from graphene.query.planner import QueryPlanner

class MatchCommand(Command):
    def __init__(self, node_chain, query_chain, optional_clauses):
        self.nc = node_chain
        self.qc = query_chain
        self.rc, self.limit, self.orderby = self.parse_clauses(optional_clauses or [])

    def parse_clauses(self, clauses):
        """
        We have to sanitize these optional clauses. Since they can come in any
        order, the cleanest way to parse the tree is to allow any number of them
        and ensure that there are no more than 1 of each type.
        """
        ctr = Counter(clause_type for clause_type, clause_value in clauses)
        if ctr[OptionalClause.ORDERBY] > 1:
            raise TooManyClausesException("There are too many ORDER BY clauses."
                " Only one ORDER BY clause is permitted.")
        if ctr[OptionalClause.RETURN] > 1:
            raise TooManyClausesException("There are too many RETURN clauses."
                " Only one RETURN clause is permitted.")
        if ctr[OptionalClause.LIMIT] > 1:
            raise TooManyClausesException("There are too many LIMIT clauses."
                " Only one LIMIT clause is permitted.")
        clauses = dict(clauses)

        rc = clauses[OptionalClause.RETURN] \
            if OptionalClause.RETURN in clauses else ()
        limit = clauses[OptionalClause.LIMIT] \
            if OptionalClause.LIMIT in clauses else 0
        if limit < 0:
            # No negative limits
            limit = 0
        orderby = clauses[OptionalClause.ORDERBY] \
            if OptionalClause.ORDERBY in clauses else []
        return (rc, limit, orderby)

    def __repr__(self):
        lst = ["\t%s" % chain for chain in self.nc]
        return "[Match\n%s\n]" % "\n".join(lst)

    def execute(self, storage_manager, output=sys.stdout, timer=None):
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

        if timer is not None:
            timer.pause() # pause timer for printing
        # If there's nothing found, there were no nodes
        if len(results) == 0:
            printer.print_info("No results found.\n", output)
            return []

        printer.print_table(results, schema, output)
        printer.print_info("%d result(s) found.\n" % len(results))
        return results
