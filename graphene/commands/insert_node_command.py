from __future__ import print_function
from graphene.commands.command import Command
from graphene.storage import Property
from graphene.utils.conversion import TypeConversion
from graphene.errors import BadPropertyException, TypeMismatchException
import logging

class InsertNodeCommand(Command):
    def __init__(self, node_prop_list):
        self.node_prop_list = node_prop_list
        self.logger = logging.getLogger(self.__class__.__name__)

    def execute(self, storage_manager):
        final_types, final_props = [], []
        self.logger.debug("node_prop_list: " % self.node_prop_list)
        for nodeprop in self.node_prop_list:
            type_name, prop_list = nodeprop.t, nodeprop.pl or []
            node_type, schema = storage_manager.get_node_data(type_name)
            properties = []
            num_props, schema_len = len(prop_list), len(schema)
            if num_props != schema_len:
                raise BadPropertyException("Expected %d propert%s, but got %d." % \
                    (schema_len, "y" if schema_len == 1 else "ies", num_props))
            for prop, schema_tt in zip(prop_list, schema):
                tt, prop_name, exp_tt = schema_tt

                # Get the type of the inputted property and compare it to the
                # type we're expecting
                if prop == "[]":
                    # empty array, so we just have to check that the expected
                    # type is some time of array
                    if exp_tt.value < Property.PropertyType.intArray.value:
                        raise TypeMismatchException("Got empty array, but " \
                                "expected value of type %s for property '%s'." \
                                % (exp_tt, prop_name))
                    conv_value = []
                else:
                    given_type = TypeConversion.get_type_type_of_string(prop)
                    if given_type != exp_tt:
                        err = "Got value of type %s, but expected value of "\
                                "type %s for property '%s'." % (given_type,
                                    exp_tt, prop_name)
                        raise TypeMismatchException(err)
                    # Convert value and add to list
                    conv_value = TypeConversion.convert_to_value(prop, given_type)
                    self.logger.debug("\t\t%s, %s" %(str(conv_value),
                                                     str(given_type)))
                properties.append((exp_tt, conv_value))
            final_types.append(node_type)
            final_props.append(properties)
        for node_type, properties in zip(final_types, final_props):
            self.logger.debug("Node type names: %s" % dir(node_type))
            self.logger.debug("properties: %s" % properties)

            storage_manager.insert_node(node_type, properties)
