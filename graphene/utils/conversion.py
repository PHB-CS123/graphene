from graphene.storage import Property

class TypeConversion:
    @staticmethod
    def convert_to_value(s, given_type):
        if given_type.name.find("Array") > -1:
            # array type! so just map
            base_type = Property.PropertyType[given_type.name.replace("Array", "")]
            if s == "[]":
                return []
            else:
                return map(lambda v: TypeConversion.convert_to_value(v,
                    base_type), s[1:-1].split(","))
        elif given_type == Property.PropertyType.bool:
            if s.upper() == "TRUE":
                return True
            return False
        elif given_type == Property.PropertyType.float:
            return float(s)
        elif given_type == Property.PropertyType.int:
            return int(s)
        elif given_type == Property.PropertyType.string:
            return s[1:-1]

    @staticmethod
    def get_type_type_of_string(s):
        if s[0] == "[" and s[-1] == "]":
            if len(s) == 2:
                # empty array, so undefined
                return Property.PropertyType.undefined
            # Get rid of superfluous whitespace
            values = map(lambda s: s.strip(), s[1:-1].split(","))
            # Convert everything in this array to a type
            all_types = map(TypeConversion.get_type_type_of_string, values)
            # If everything is of the same type, return array version of that
            # type. Otherwise undefined
            if all_types.count(all_types[0]) == len(all_types):
                return Property.PropertyType[all_types[0].name + "Array"]
            else:
                return Property.PropertyType.undefined
        elif s.upper() == "TRUE" or s.upper() == "FALSE":
            return Property.PropertyType.bool
        elif s.count(".") == 1 and (all(v.isdigit() for v in s.split(".")) or (
                (s[0] == '-' or s[0] == '+') and all(v.isdigit() for v in s[1:].split(".")))):
            return Property.PropertyType.float
        elif s.isdigit() or \
            ((s[0] == '-' or s[0] == '+') and s[1:].isdigit()):
            return Property.PropertyType.int
        elif s[0] == '"' and s[-1] == '"':
            return Property.PropertyType.string
        else:
            return Property.PropertyType.undefined
