from __future__ import print_function
from graphene.commands.command import Command
from graphene.storage import Property
from graphene.utils.conversion import TypeConversion
import logging

class InsertNodeCommand(Command):
    def __init__(self, node_prop_list):
        self.node_prop_list = node_prop_list
        self.logger = logging.getLogger(self.__class__.__name__)

    def execute(self, storage_manager):
        final_types, final_props = [], []
        self.logger.debug("node_prop_list: " % self.node_prop_list)
        for nodeprop in self.node_prop_list:
            type_name, prop_list = nodeprop.t, nodeprop.pl
            node_type, schema = storage_manager.get_node_data(type_name)
            properties = []
            for prop, schema_tt in zip(prop_list, schema):
                tt, prop_name, exp_tt = schema_tt

                # Get the type of the inputted property and compare it to the
                # type we're expecting
                given_type = TypeConversion.get_type_type_of_string(prop)
                expected_type = exp_tt
                if given_type != expected_type:
                    raise Exception("Got value of type %s, but expected value "
                                    "of type %s for property '%s'." %
                                    (given_type, expected_type, prop_name))
                # Convert value and add to list
                conv_value = storage_manager.convert_to_value(prop, given_type)
                properties.append((given_type, conv_value))
            final_types.append(node_type)
            final_props.append(properties)
        for node_type, properties in zip(final_types, final_props):
            self.logger.debug("Node type names: %s" % dir(node_type))
            self.logger.debug("properties: %s" % properties)

            storage_manager.insert_node(node_type, properties)
