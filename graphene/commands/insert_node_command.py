from graphene.commands.command import Command
from graphene.storage import Property

class InsertNodeCommand(Command):
    def __init__(self, node_prop_list):
        self.node_prop_list = node_prop_list

    def get_type_type_of_string(self, s):
        if s.upper() == "TRUE" or s.upper() == "FALSE":
            return Property.PropertyType.bool
        if s.isdigit():
            return Property.PropertyType.int
        if s[0] == '"' and s[-1] == '"':
            return Property.PropertyType.string
        return Property.PropertyType.undefined

    def convert_to_value(self, s, given_type):
        if given_type == Property.PropertyType.bool:
            if s.upper() == "TRUE":
                return True
            return False
        if given_type == Property.PropertyType.int:
            return int(s)
        if given_type == Property.PropertyType.string:
            return s[1:-1]

    def execute(self, storage_manager):
        final_types, final_props = [], []
        for nodeprop in self.node_prop_list:
            type_name, prop_list = nodeprop.t, nodeprop.pl
            node_type, schema = storage_manager.get_type_data(type_name)
            properties = []
            for prop, exp_type_type in zip(prop_list, schema):
                given_type = self.get_type_type_of_string(prop)
                expected_type = exp_type_type.propertyType
                prop_name = storage_manager.type_type_name_manager.read_name_at_index(exp_type_type.typeName)
                if given_type != expected_type:
                    raise Exception("Got value of type %s, but expected value of type %s for property '%s'." %
                          (given_type, expected_type, prop_name))
                properties.append((given_type, self.convert_to_value(prop, given_type)))
            final_types.append(node_type)
            final_props.append(properties)
        for node_type, properties in zip(final_types, final_props):
            storage_manager.insert_node(node_type, properties)
