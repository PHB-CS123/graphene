import sys
from enum import Enum
import logging

from graphene.commands.command import Command
from graphene.errors import TypeDoesNotExistException
from graphene.utils import PrettyPrinter
from graphene.storage import GeneralStore

class DescCommand(Command):
    class DescType(Enum):
        TYPE = 1
        RELATION = 2

    def __init__(self, type_name, desc_type):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.type_name = type_name
        self.desc_type = desc_type

        self.logger.debug("Describing type with name: %s" % type_name)

    def execute(self, storage_manager, output=sys.stdout):
        try:
            if self.desc_type == DescCommand.DescType.TYPE:
                type_data, type_schema = storage_manager.get_node_data(self.type_name)
            else:
                type_data, type_schema = storage_manager.get_relationship_data(self.type_name)
            values = [(tt_name, tt_type.name) for tt, tt_name, tt_type in type_schema]
            PrettyPrinter.print_table(values, header=("Name", "Type"), output=output)
        except TypeDoesNotExistException as e:
            # If type doesn't exist, just print out error since this is a debug
            # command
            PrettyPrinter.print_error(e, output)
