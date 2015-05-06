from graphene.traversal import *
from graphene.query import ProjectStream
from graphene.expressions import MatchNode, MatchRelation
from graphene.errors import *

class QueryPlanner:
    def __init__(self, storage_manager):
        self.sm = storage_manager

    def reduce_query_chain(self, query_chain, schema, alias=None, throw=False):
        """
        Reduce a set of queries such that they only apply to the given schema.
        """
        new_chain = []
        base_names = [n.split(".")[-1] for n, t in schema]
        for qc in query_chain:
            # Boolean logic, ignore for now
            if type(qc) != tuple:
                continue
            # If the identifier doesn't exist or matches the alias given, check
            # that the name is in base_names. Note that we do not check for
            # duplicates! That is handled elsewhere.
            elif (qc[0] == alias or qc[0] is None) and qc[1] in base_names:
                new_chain.append(qc)
            # TODO: Do we need this? So far nothing ever passes True to throw...
            elif throw:
                raise NonexistentPropertyException("No such property name: " + qc[1])
        return Query.parse_chain(self.sm, new_chain, schema)

    def create_relation_tree(self, node_chain, query_chain):
        # If there's only one thing in the node chain, it's a node selector, so
        # we create a NodeIterator to iterate over that query
        if len(node_chain) == 1:
            node = node_chain[0]
            schema = self.get_schema(node_chain)
            qc = self.reduce_query_chain(query_chain, schema, node.name)
            return NodeIterator(self.sm, node, schema, qc)
        # Otherwise we want to create a RelationIterator
        else:
            full_schema = self.get_schema(node_chain)

            # Get right schema and query chain, reduced to the right schema
            right_schema = self.get_schema([node_chain[-1]])
            right_qc = self.reduce_query_chain(query_chain, right_schema, node_chain[-1].name)

            left, rel, right = node_chain[:-2], node_chain[-2], \
                NodeIterator(self.sm, node_chain[-1], right_schema, right_qc)

            # Get relation schema and query chain, reduced to the right schema
            rel_schema = self.get_schema([rel])
            rel_qc = self.reduce_query_chain(query_chain, rel_schema, rel.name)

            return RelationIterator(self.sm, rel,
                self.create_relation_tree(left, query_chain), right, rel_schema, rel_qc)

    def get_schema(self, node_chain, fullset=False):
        schema = []
        sub_schemas = []
        schema_keys = []

        # Pull some info out of the node chain, since we only care about the
        # schemas
        for nc in node_chain:
            if isinstance(nc, MatchNode):
                schema_data = self.sm.get_node_data(nc.type)[1]
            else:
                schema_data = self.sm.get_relationship_data(nc.type)[1]
            sub_schemas.append((schema_data, nc.name is not None, nc.name))

        # Check whether everything in our query is unidentified (so we actually
        # care about duplicates)
        all_unidentified = not any(identified for _, identified, __ in sub_schemas)
        for schema_data, identified, ident in sub_schemas:
            for tt, tt_name, tt_type in schema_data:
                # If the key is identified, we prefix it with the identifier
                if not identified:
                    key = tt_name
                    # If all nodes/relations are unidentified and there's a
                    # duplicate, throw an error. We also only want to do this
                    # when we are told that this is the full set of schema data,
                    # not just a subset, since we only care about there being
                    # duplicates at the end. Otherwise this is ok.
                    if all_unidentified and key in schema_keys and fullset:
                        raise DuplicatePropertyException("Duplicate property name `%s` in query. " \
                            "Try adding an identifier." % key)
                else:
                    key = "%s.%s" % (ident, tt_name)
                    if key in schema_keys:
                        raise DuplicatePropertyException("Duplicate property name `%s` in query. " \
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
            # If there is an identifier, check that the requested property
            # exists in the schema
            if qc[0] is not None:
                key = "%s.%s" % (qc[0], qc[1])
                if key not in schema_names:
                    raise NonexistentPropertyException("Property name `%s` does not exist." % key)
            # Otherwise check the base names
            else:
                num_occur = base_names.count(qc[1])
                # Occurs more than once, it's ambiguous
                if num_occur > 1:
                    raise AmbiguousPropertyException("Property name `%s` is ambiguous. Please add an identifier." % qc[1])
                elif num_occur == 0:
                    raise NonexistentPropertyException("Property name `%s` does not exist." % qc[1])

    def execute(self, node_chain, query_chain, return_chain):
        if query_chain is None:
            query_chain = ()
        if return_chain is None:
            return_chain = ()
        # Gather schema information from node chain. Collects all property names
        schema = self.get_schema(node_chain, fullset=True)

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

        num_unidentified = [nc.name for nc in node_chain].count(None)

        # If we have explicit projects, or unidentified nodes/relations, then we
        # will do a project. If everything is unidentified, then we just show
        # all the base names (i.e. without identifiers)
        if len(return_chain) > 0 or len(node_chain) > num_unidentified > 0:
            stream = ProjectStream(return_chain, schema, results)
            schema_names = stream.schema_names
            results = list(stream)

        return (schema_names, results)
