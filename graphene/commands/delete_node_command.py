import sys

from graphene.commands.command import Command
from graphene.expressions.match_node import MatchNode
from graphene.query.planner import QueryPlanner

class DeleteNodeCommand(Command):
    """
    Used to delete individual nodes from the database.
    """
    def __init__(self, data):
        self.node_type = data.t
        self.qc = data.q

    def execute(self, storage_manager, output=sys.stdout, timer=None):
        planner = QueryPlanner(storage_manager)
        # Iterate over nodes using the planner's helper method for convenience
        iter_tree = planner.get_iter_tree([MatchNode(None, self.node_type)],
                                          self.qc)
        for nodeprop in iter_tree:
            del storage_manager.nodeprop[nodeprop.node.index]
