from graphene.traversal import *
from graphene.query import ProjectStream
from graphene.expressions import MatchNode, MatchRelation
from graphene.errors import *

class PlannerErrors:
    """
    A class to store common errors in the query planner
    """
    @staticmethod
    def property_dne(name):
        """
        The desired property does not exist.
        """
        msg = "Property name `%s` does not exist."
        return NonexistentPropertyException(msg % name)

    @staticmethod
    def ambiguous_prop(name):
        """
        The property name given is ambiguous and cannot uniquely define a
        property for the query.
        """
        msg = "Property name `%s` is ambiguous. Please add an identifier."
        return AmbiguousPropertyException(msg % name)

    @staticmethod
    def duplicate_prop(name):
        """
        Two properties have identical names, potentially due to using the same
        identifier.
        """
        msg = "Duplicate property name `%s` in query. Try adding an identifier."
        return DuplicatePropertyException(msg % name)

class QueryPlanner:
    def __init__(self, storage_manager):
        self.sm = storage_manager

    def create_relation_tree(self, node_chain):
        """
        Creates a binary tree corresponding to how we will traverse relations.
        All leafs are node iterators, and all non-leafs are relation iterators.
        Determines which subtrees queries apply to and restricts them
        accordingly so less query testing needs to be done.
        """
        # If there's only one thing in the node chain, it's a node selector, so
        # we create a NodeIterator to iterate over that query
        if len(node_chain) == 1:
            node = node_chain[0]
            schema = self.get_schema(node_chain)
            return NodeIterator(self.sm, node, schema, None)
        # Otherwise we want to create a RelationIterator
        else:
            full_schema = self.get_schema(node_chain)

            # Get right schema and query chain, reduced to the right schema
            right_schema = self.get_schema([node_chain[-1]])

            left, rel, right = node_chain[:-2], node_chain[-2], \
                NodeIterator(self.sm, node_chain[-1], right_schema, None)

            # Get relation schema and query chain, reduced to the right schema
            rel_schema = self.get_schema([rel])

            return RelationIterator(self.sm, rel,
                self.create_relation_tree(left), right)

    def get_schema(self, node_chain, fullset=False):
        """
        Calculates the schema of a given node chain. If fullset is set to True,
        that implies that the node chain provided is that of the entire query,
        so we actually care about ambiguous/duplicate unidentified property
        names. If we are only acting on a subset, we don't worry about
        unidentified names because they will be ignored in a later projection.
        """
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
                        raise PlannerErrors.duplicate_prop(key)
                else:
                    key = "%s.%s" % (ident, tt_name)
                    if key in schema_keys:
                        raise PlannerErrors.duplicate_prop(key)

                schema_keys.append(key)
                schema.append((key, tt_type))

        return schema

    def check_query(self, schema, query_chain):
        """
        Checks a given query chain for validity given a schema; ensures that the
        queries do not refer to ambiguous or nonexistent property names in the
        schema.
        """
        schema_names = [n for n, tt in schema]
        base_names = [n.split(".")[-1] for n, tt in schema]
        if query_chain is None:
            # Nothing to check!
            return
        for qc in query_chain:
            if type(qc) != tuple:
                # Boolean logic, ignore for now
                continue
            left, test, right = qc
            # If there is an identifier, check that the requested property
            # exists in the schema
            if left[0] is not None:
                key = "%s.%s" % (left[0], left[1])
                if key not in schema_names:
                    raise PlannerErrors.property_dne(key)
            # Otherwise check the base names
            if type(right) is tuple:
                # Checking with an identifier
                if right[0] is not None:
                    key = "%s.%s" % (right[0], right[1])
                    if key not in schema_names:
                        raise PlannerErrors.property_dne(key)
            # Then check base names for left and right
            if left[0] is None:
                num_occur = base_names.count(left[1])
                # Occurs more than once, it's ambiguous
                if num_occur > 1:
                    raise PlannerErrors.ambiguous_prop(left[1])
                elif num_occur == 0:
                    raise PlannerErrors.property_dne(left[1])
            if type(right) is tuple and right[0] is None:
                num_occur = base_names.count(right[1])
                # Occurs more than once, it's ambiguous
                if num_occur > 1:
                    raise PlannerErrors.ambiguous_prop(right[1])
                elif num_occur == 0:
                    raise PlannerErrors.property_dne(right[1])

    def get_iter_tree(self, node_chain, query_chain):
        """
        Generate a traversal tree and apply queries to it. Helper method for
        execution but also used elsewhere when iteration is needed.
        """
        schema = self.get_schema(node_chain, fullset=True)

        # Generate traversal tree
        iter_tree = self.create_relation_tree(node_chain)

        # Apply query to tree if the query exists
        query = Query.parse_chain(self.sm, query_chain, schema)
        if query is not None:
            query.apply_to(iter_tree)

        return iter_tree

    def get_orderby_fn(self, schema, chain):
        schema_names = [name for name, ttype in schema]
        schema_base_names = [name.split(".")[-1] for name, ttype in schema]
        indexes = []
        for full_name, direction in chain:
            if direction is None:
                direction = 'ASC'
            multiplier = 1 if direction == 'ASC' else -1
            ident, name = full_name
            if ident is None:
                if schema_base_names.count(name) > 1:
                    raise AmbiguousPropertyException("Property name `%s` is ambiguous." % name)
                elif name not in schema_base_names:
                    raise NonexistentPropertyException("Property name `%s` does not exist." % name)
                else:
                    indexes.append((schema_base_names.index(name), multiplier))
            else:
                key = "%s.%s" % r
                if key not in schema_names:
                    raise NonexistentPropertyException("Property name `%s` does not exist." % key)
                else:
                    indexes.append((schema_names.index(key), multiplier))
        def cmp_fn(a, b):
            for i, direction in indexes:
                value = cmp(a.properties[i], b.properties[i])
                if value != 0:
                    return value * direction
            return 0
        return cmp_fn

    def execute(self, node_chain, query_chain, return_chain, limit=0,
                orderby=None):
        """
        Executes a query plan given a node chain, query chain and return chain.
        Handles any projection necessary and creates a relation tree for
        traversal.
        """
        if return_chain is None:
            return_chain = ()
        if orderby is None:
            orderby = []

        # Gather schema information from node chain. Collects all property names
        schema = self.get_schema(node_chain, fullset=True)

        # Check query against schema to ensure no ambiguous or nonexistent
        # properties are being queried
        schema_names = [n for n, tt in schema]
        self.check_query(schema, query_chain)

        iter_tree = self.get_iter_tree(node_chain, query_chain)

        if len(orderby) > 0:
            cmp_fn = self.get_orderby_fn(schema, orderby)
            iter_tree = sorted(iter_tree, cmp=cmp_fn)

        # Gather results
        results = []

        # TODO: Make it so NodeIterator and RelationIterator return same
        # kind of thing (i.e. RI returns (props, rightNode), NI returns a
        # NodeProperty instance)
        i = 0
        if len(node_chain) == 1:
            # Node iterator returns slightly diff. struct. than Rel. iterator
            for nodeprop in iter_tree:
                if limit > 0 and i >= limit:
                    break
                results.append(nodeprop.properties)
                i += 1
        else:
            for props, right in iter_tree:
                if limit > 0 and i >= limit:
                    break
                results.append(props)
                i += 1

        num_unidentified = [nc.name for nc in node_chain].count(None)

        # If we have explicit projects, or unidentified nodes/relations, then we
        # will do a project. If everything is unidentified, then we just show
        # all the base names (i.e. without identifiers)
        if len(return_chain) > 0 or len(node_chain) > num_unidentified > 0:
            stream = ProjectStream(return_chain, schema, results)
            schema_names = stream.schema_names
            results = list(stream)

        return (schema_names, results)
