import abc
from graphene.storage import Property


class Command(object):

    # Used to indicate abstract methods
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, ctx):
        raise NotImplementedError

    def __repr__(self):
        return "[Command]"

    def execute(self, storage_manager):
        print "executing..."

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
