from graphene.commands.command import Command
from graphene.expressions import *
from graphene.traversal import Query
from graphene.query.planner import QueryPlanner

class DeleteRelationCommand(Command):
    def __init__(self, data):
        self.rel_type = data.t
        self.qc = data.q

    def execute(self, storage_manager):
        planner = QueryPlanner(storage_manager)
        rel_schema = planner.get_schema([MatchRelation(None, self.rel_type)])
        schema_names = map(lambda p: p[0], rel_schema)
        q = Query.parse_chain(storage_manager, self.qc, rel_schema)
        rel_type, schema = storage_manager.get_relationship_data(self.rel_type)
        for relprop in storage_manager.get_relations_of_type(rel_type):
            if q is not None:
                zipped = zip(rel_schema, relprop.properties)
                prop_dict = dict((sch[0], (value, sch[1])) for sch, value in zipped)
                if not q.test(prop_dict):
                    continue
            del storage_manager.relprop[relprop.rel.index]
