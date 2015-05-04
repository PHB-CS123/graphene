from graphene.traversal import *
from graphene.query import ProjectStream
from graphene.expressions import MatchNode, MatchRelation

class QueryPlanner:
    def __init__(self, storage_manager):
        self.sm = storage_manager

    def reduce_query_chain(self, query_chain, schema, alias=None, throw=False):
        new_chain = []
        base_names = [n.split(".")[-1] for n, t in schema]
        for qc in query_chain:
            if type(qc) != tuple:
                # Boolean logic, ignore for now
                continue
            elif (qc[0] == alias and qc[1] in base_names) \
                or (qc[0] == None and qc[1] in base_names):
                new_chain.append(qc)
            elif throw:
                raise Exception("No such property name: " + qc[1])
        return Query.parse_chain(self.sm, new_chain, schema)

    def create_relation_tree(self, node_chain, query_chain):
        if len(node_chain) == 1:
            node = node_chain[0]
            schema = self.get_schema(node_chain)
            qc = self.reduce_query_chain(query_chain, schema, node.name)
            return NodeIterator(self.sm, node, schema, qc)
        else:
            full_schema = self.get_schema(node_chain)
            right_schema = self.get_schema([node_chain[-1]])
            right_qc = self.reduce_query_chain(query_chain, right_schema, node_chain[-1].name)
            left, rel, right = node_chain[:-2], node_chain[-2], \
                NodeIterator(self.sm, node_chain[-1], right_schema, right_qc)
            rel_schema = self.get_schema([rel])
            rel_qc = self.reduce_query_chain(query_chain, rel_schema, rel.name)
            return RelationIterator(self.sm, rel,
                self.create_relation_tree(left, query_chain), right, rel_schema, rel_qc)

    def get_schema(self, node_chain):
        schema = []
        schema_keys = []
        for nc in node_chain:
            if isinstance(nc, MatchNode):
                schema_data = self.sm.get_node_data(nc.type)[1]
            else:
                schema_data = self.sm.get_relationship_data(nc.type)[1]
            for tt, tt_name, tt_type in schema_data:
                if nc.name is None:
                    key = tt_name
                else:
                    key = "%s.%s" % (nc.name, tt_name)
                if key in schema_keys:
                    raise Exception("Duplicate property name `%s` in query. " \
                        "Try adding an identifier." % key)
                schema_keys.append(key)
                schema.append((key, tt_type))
        return schema

    def check_query(self, schema, node_chain, query_chain):
        schema_names = [n for n, tt in schema]
        base_names = [n.split(".")[-1] for n, tt in schema]
        for qc in query_chain:
            if type(qc) != tuple:
                # Boolean logic, ignore for now
                continue
            if qc[0] is not None:
                key = "%s.%s" % (qc[0], qc[1])
                if key not in schema_names:
                    raise Exception("Property name `%s` does not exist." % key)
            else:
                num_occur = base_names.count(qc[1])
                # Occurs more than once, it's ambiguous
                if num_occur > 1:
                    raise Exception("Property name `%s` is ambiguous. Please add an identifier." % qc[1])
                elif num_occur == 0:
                    raise Exception("Property name `%s` does not exist." % qc[1])

    def execute(self, node_chain, query_chain, return_chain):
        # Gather schema information from node chain. Collects all property names
        schema = self.get_schema(node_chain)

        # Check query against schema to ensure no ambiguous or nonexistent properties are being queried
        schema_names = [n for n, tt in schema]
        self.check_query(schema, node_chain, query_chain)

        # Gather results
        results = []

        # TODO: Make it so NodeIterator and RelationIterator return same
        # kind of thing (i.e. RI returns (props, rightNode), NI returns a
        # NodeProperty instance)
        if len(node_chain) == 1:
            # NodeIterator returns slightly different structure than RelationshipIterator
            for nodeprop in self.create_relation_tree(node_chain, query_chain):
                results.append(nodeprop.properties)
        else:
            for props, right in self.create_relation_tree(node_chain, query_chain):
                results.append(props)

        if len(return_chain) > 0:
            stream = ProjectStream(return_chain, schema, results)
            schema_names = stream.schema_names
            results = list(stream)

        # TODO: Strip property columns where the node/relation was not supplied
        # an alias
        return (schema_names, results)
