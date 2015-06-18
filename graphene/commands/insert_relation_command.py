from graphene.commands.command import Command
from graphene.storage import StorageManager
from graphene.expressions import *
from graphene.traversal import *
from graphene.utils.conversion import TypeConversion
from graphene.errors import TypeMismatchException, BadPropertyException
import logging

import itertools

class InsertRelationCommand(Command):
    def __init__(self, ctx):
        self.relprops = ctx
        self.logger = logging.getLogger(self.__class__.__name__)

    def parse_properties(self, prop_list, schema, storage_manager):
        """
        Takes a list of properties that are intended to be inserted into the
        relation, check that they match the schema of the relation (in order),
        and then convert them to the desired type.

        :type prop_list: list
        :param prop_list: list of properties
        :type schema: list
        :param schema: list of tuples (type-type, property name, expected type)
        :type storage_manager: StorageManager
        :param storage_manager: storage manager for the calling instance
        :return: List of properties
        """
        properties = []
        schema_len = len(schema)
        num_props = len(prop_list)
        if num_props != schema_len:
            raise BadPropertyException("Expected %d propert%s, but got %d." % \
                (schema_len, "y" if schema_len == 1 else "ies", num_props))
        for prop, schema_tt in zip(prop_list, schema):
            tt, prop_name, expected_type = schema_tt
            given_type = TypeConversion.get_type_type_of_string(prop)
            if given_type != expected_type:
                raise TypeMismatchException("Got value of type %s, but"
                            " expected value of type %s for property '%s'." %
                            (given_type, expected_type, prop_name))
            conv_value = TypeConversion.convert_to_value(prop, given_type)
            properties.append((given_type, conv_value))
        return properties

    def prop_to_dict(self, props, schema):
        """
        Converts the provided property list into a dict corresponding to the key
        names (which may have identifiers)
        """
        result = {}
        for i, tt_data in enumerate(schema):
            tt, name, tt_type = tt_data
            # If there is an alias, create a key from it; i.e. if the type
            # identifier is t, then t.a works.
            result[name] = (props[i], tt_type)
        return result

    def execute(self, storage_manager, timer=None):
        """
        Inserts a relationship into the storage layer.

        :type storage_manager: StorageManager
        :param storage_manager: storage manager for this instance
        :return: List of inserted relations
        """
        relation_info = []
        left_queries = []
        right_queries = []
        type_names = {}

        inserted_relations = []
        for rel, query1, query2 in self.relprops:
            # Gather information about the relation: name, type, schema and properties
            rel_name = rel[0]
            rel_type, rel_schema = storage_manager.get_relationship_data(rel_name)
            rel_props = self.parse_properties(rel[1] or [], rel_schema, storage_manager)

            # Determine type and schema information for type 1 (the left side of the
            # relation)
            type1, queries1 = query1
            type_data1, type_schema_data1 = storage_manager.get_node_data(type1)
            type_schema1 = [(tt_name, tt_type) for _, tt_name, tt_type in type_schema_data1]

            # Determine type and schema information for type 2
            # (the right side of the relation)
            type2, queries2 = query2
            type_data2, type_schema_data2 = storage_manager.get_node_data(type2)
            type_schema2 = [(tt_name, tt_type) for _, tt_name, tt_type in type_schema_data2]

            # Parse queries for the left and right nodes
            qc1 = Query.parse_chain(storage_manager, queries1, type_schema1)
            qc2 = Query.parse_chain(storage_manager, queries2, type_schema2)

            # Store this data in a place for later usage; we just want to know
            # which queries were on either side of a relation
            left_queries.append((qc1, type_data1.index))
            right_queries.append((qc2, type_data2.index))
            relation_info.append({
                "name": rel_name,
                "type": rel_type,
                "props": rel_props,
                "left": [],
                "right": []
            })
            type_names[type1] = (type_data1, type_schema_data1)
            type_names[type2] = (type_data2, type_schema_data2)

        # Iterate through each needed node type ONCE and do all queries there;
        # this puts the relevant nodes on the correct side of their relation
        # if they apply.
        for tn, t in type_names.items():
            td, t_sch = t
            for np in storage_manager.get_nodes_of_type(td):
                nodeType = np.node.nodeType
                props = self.prop_to_dict(np.properties, t_sch)
                for i, lr in enumerate(zip(left_queries, right_queries)):
                    l_pair, r_pair = lr

                    # Check left side
                    l_query, l_type = l_pair
                    if l_type == nodeType and l_query.test(props):
                        relation_info[i]["left"].append(np.node)

                    # Check right side
                    r_query, r_type = r_pair
                    if r_type == nodeType and r_query.test(props):
                        relation_info[i]["right"].append(np.node)

        # Actually insert the relations here
        for rel_info in relation_info:
            rel_name = rel_info["name"]
            rel_type = rel_info["type"]
            rel_props = rel_info["props"]
            pairs = itertools.product(rel_info["left"], rel_info["right"])
            # Iterate over a product of the left node-set and right node-set. For
            # each, we will create a relation. We don't care if a node appears on
            # both sides; that's fine.
            for left_node, right_node in pairs:
                if left_node == right_node:
                    continue

                self.logger.debug("Inserting relation %s between %s and %s"
                                  % (rel_name, left_node, right_node))
                rel = storage_manager.insert_relation(rel_type, rel_props,
                    left_node, right_node)
                inserted_relations.append(rel)

        return inserted_relations
