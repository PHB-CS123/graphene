from enum import Enum
from ConfigParser import ConfigParser, NoSectionError
import logging
import os

from graphene.storage.base import GrapheneStore


class ConfigStore(object):
    CONF_FILENAME = "default.conf"

    class ConfigType(Enum):
        """ Configuration value type. """
        undefined = 0
        int = 1
        bool = 2
        string = 3

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.file_path = GrapheneStore().datafilesDir + self.CONF_FILENAME
        try:
            # If no config file exists, create one
            if not os.path.isfile(self.file_path):
                open(self.file_path, "w+").close()
            self.config = ConfigParser()
            self.config.read(self.file_path)
        except IOError:
            raise IOError("ERROR: unable to open file: " + self.file_path)

    def __del__(self):
        """ Writes configs back to the config file """
        config_file = open(self.file_path, "w")
        self.config.write(config_file)
        config_file.close()

    def get_config(self, name, config_type, section="Main"):
        """
        Get the value for the given config name

        :param name: Name of the value to get
        :type name: str
        :param config_type: Type of value
        :type config_type: ConfigStore.ConfigType
        :param section: Section where the value is located
        :type section: str
        :return: Value for the config
        :rtype: int | bool | str
        """
        values = self.config_section_map(section)
        if not values:
            return None
        try:
            value = values[name.lower()]
        except KeyError:
            return None
        return self.convert_value_to_type(value, config_type)

    def set_config(self, name, value, section="Main"):
        """
        Set the value for the given config name

        :param name: Name of the value to set
        :type name: str
        :param value: Value for the given name
        :type value: int | bool | str
        :param section: Section to write the value to
        :type section: str
        :return: Nothing
        :rtype: None
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, name.lower(), value)

    def convert_value_to_type(self, value, config_type):
        """
        Convert the given value to the config type

        :param value: Value to convert
        :type value: str
        :param config_type: Config type to convert to
        :type config_type: ConfigStore.ConfigType
        :return: Converted value
        :rtype: int | bool | str
        """
        if config_type is self.ConfigType.int:
            return int(value)
        elif config_type is self.ConfigType.bool:
            return True if value == str(True) else False
        elif config_type is self.ConfigType.string:
            return value
        else:
            raise TypeError("Unhandled ConfigType: %s" % config_type)

    def config_section_map(self, section):
        """
        Get a dictionary with the values for the given section

        :param section: Section to get values for
        :type section: str
        :return: Dictionary mapping names to values for the section
        :rtype: dict[str, str]
        """
        values = {}
        try:
            options = self.config.options(section)
        except NoSectionError:
            return None

        for option in options:
            values[option] = self.config.get(section, option)
            if values[option] == -1:
                self.logger.debug("Unable to find section: %s" % option)
        return values
