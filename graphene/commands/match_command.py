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
        # if len(self.rc) == 0:
        #     # If there's no return statement, we do nothing to the columns
        #     return_filter = lambda x: x
        # else:
        #     indexes = []
        #     schema_names = [name for tt, name, ttype in type_schema]
        #     for r in self.rc:
        #         ident, name = r
        #         # If there is an identifier given (e.g. `MATCH (a:A)`), then we
        #         # check that if one was given with the return query that it
        #         # matches the one we are looking at with the current schema.
        #         # That is, if our selection is `MATCH (a:A)`, where A has fields
        #         # b or c, then `RETURN b, c` and `RETURN a.b, a.c` both work and
        #         # do the same thing, but `RETURN a` and `RETURN t.b` do not.
        #         if (ident == alias or ident is None) and name in schema_names:
        #             indexes.append(schema_names.index(name))
        #     return_filter = lambda l: [l[i] for i in indexes]

        # # Filter out the header columns with respect to the RETURN clause, if
        # # one was provided
        # header = return_filter([name.upper() for tt, name, ttype in type_schema])

        # # We use a NodeIterator here to loop through the table. TODO: Determine
        # # whether we want to put return filtering in the iterator or just do it
        # # afterwards
        # iterator = NodeIterator(storage_manager, type_data, type_schema,
        #                         alias, qc)

        # values = []
        # for node in iterator:
        #     values.append(return_filter(node.properties))

        # If there's nothing found, there were no nodes
        if len(results) == 0:
            output.write("No nodes found.\n")
            return []

        PrettyPrinter.print_table(results, schema, output)
        return results
