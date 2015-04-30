from __future__ import print_function
from graphene.commands.command import Command
from graphene.storage import Property

class InsertNodeCommand(Command):
    def __init__(self, node_prop_list):
        self.node_prop_list = node_prop_list

    def execute(self, storage_manager):
        final_types, final_props = [], []
        print("node_prop_list:", self.node_prop_list)
        for nodeprop in self.node_prop_list:
            type_name, prop_list = nodeprop.t, nodeprop.pl
            node_type, schema = storage_manager.get_node_data(type_name)
            properties = []
            for prop, schema_tt in zip(prop_list, schema):
                tt, prop_name, exp_tt = schema_tt
                given_type = self.get_type_type_of_string(prop)
                expected_type = exp_tt
                if given_type != expected_type:
                    raise Exception("Got value of type %s, but expected value "
                                    "of type %s for property '%s'." %
                                    (given_type, expected_type, prop_name))
                conv_value = storage_manager.convert_to_value(prop, given_type)
                properties.append((given_type, conv_value))
            final_types.append(node_type)
            final_props.append(properties)
        for node_type, properties in zip(final_types, final_props):
            print("Node type names:", dir(node_type), "properties:", properties)
            storage_manager.insert_node(node_type, properties)

    # @staticmethod
    # def get_type_type_of_string(s):
    #     if s.upper() == "TRUE" or s.upper() == "FALSE":
    #         return Property.PropertyType.bool
    #     if s.isdigit() or \
    #         ((s[0] == '-' or s[0] == '+') and s[1:].isdigit()):
    #         return Property.PropertyType.int
    #     if s[0] == '"' and s[-1] == '"':
    #         return Property.PropertyType.string
    #     return Property.PropertyType.undefined
