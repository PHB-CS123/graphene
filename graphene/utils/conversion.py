from graphene.storage import Property

class TypeConversion:
    @staticmethod
    def get_type_type_of_string(s):
        if s.upper() == "TRUE" or s.upper() == "FALSE":
            return Property.PropertyType.bool
        if s.isdigit() or \
            ((s[0] == '-' or s[0] == '+') and s[1:].isdigit()):
            return Property.PropertyType.int
        if s[0] == '"' and s[-1] == '"':
            return Property.PropertyType.string
        return Property.PropertyType.undefined
