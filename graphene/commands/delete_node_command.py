from graphene.commands.command import Command
from graphene.expressions import MatchNode
from graphene.query.planner import QueryPlanner

class DeleteNodeCommand(Command):
    def __init__(self, data):
        self.node_type = data.t
        self.qc = data.q

    def execute(self, storage_manager):
        planner = QueryPlanner(storage_manager)
        iter_tree = planner.get_iter_tree([MatchNode(None, self.node_type)], self.qc)
        for nodeprop in iter_tree:
            del storage_manager.nodeprop[nodeprop.node.index]
