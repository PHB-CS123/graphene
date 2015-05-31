from graphene.commands.command import Command
from graphene.expressions import *
from graphene.traversal import Query
from graphene.query.planner import QueryPlanner

class UpdateRelationCommand(Command):
    """
    Used to update individual relations from the database.
    """
    def __init__(self, rel_type, query_chain, left_node, right_node, update):
        self.rel_type = rel_type
        self.qc = query_chain
        self.left_node = left_node
        self.right_node = right_node
        self.update = update
