from graphene.commands.command import Command
from graphene.expressions.match_node import MatchNode
from graphene.query.planner import QueryPlanner

class UpdateNodeCommand(Command):
    """
    Used to update nodes from the database
    """
    def __init__(self, data):
        self.node_type = data.t
        self.qc = data.q
        self.update = data.u

    def execute(self, storage_manager):
        planner = QueryPlanner(storage_manager)
        # Iterate over nodes using the planner's helper method for convenience
        iter_tree = planner.get_iter_tree([MatchNode(None, self.node_type)],
                                          self.qc)

        storage_manager.update_node(iter_tree, self.update)
