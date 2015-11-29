import sys
from graphene.commands.command import Command
# from graphene.storage.config.config_store import ConfigStore


class ConfigCommand(Command):
    def __init__(self, name, section, value):
        super(ConfigCommand, self).__init__()
        self.name = name
        self.section = section
        self.value = value

    def execute(self, storage_manager, output=sys.stdout, timer=None):
        value = self.value_from_string(self.value)
        ConfigStore().set_config(self.name, value, self.section)

    @staticmethod
    def value_from_string(string):
        """
        Returns the implied value from the given string

        :param string: String to get a primitive value for
        :type string: str
        :return: Primitive value
        :rtype: int | bool | str
        """
        # Try to convert it to an integer
        try:
            return int(string)
        except ValueError:
            pass
        # Try to convert it to a boolean, otherwise store the string
        if string.lower() == str(True).lower():
            return True
        elif string.lower() == str(False).lower():
            return False
        else:
            return string
