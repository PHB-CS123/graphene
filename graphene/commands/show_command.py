from enum import Enum
import sys

from graphene.commands.command import Command
from graphene.utils import PrettyPrinter, CmdTimer
from graphene.storage import GeneralStore
from graphene.storage import StorageManager

class ShowCommand(Command):
    class ShowType(Enum):
        TYPES = 1
        RELATIONS = 2

    def __init__(self, show_type):
        self.show_type = show_type

    def execute(self, storage_manager, output=sys.stdout, timer=CmdTimer()):
        """
        Execute the show command.
        :param storage_manager: a storage manager.
        :type storage_manager: StorageManager
        :return:
        """
        # Instance of pretty printer to use for all output
        printer = PrettyPrinter()

        # Dictionaries to determine type and name managers for various types.
        type_managers = {
            self.ShowType.TYPES: storage_manager.nodeTypeManager,
            self.ShowType.RELATIONS: storage_manager.relTypeManager
        }
        type_name_managers = {
            self.ShowType.TYPES: storage_manager.nodeTypeNameManager,
            self.ShowType.RELATIONS: storage_manager.relTypeNameManager
        }

        # Choose the type and name managers for what we are supposed to show.
        type_manager = type_managers[self.show_type]
        type_name_manager = type_name_managers[self.show_type]

        # Loop through the types and read their names into a list.
        i = 1
        name_list = []
        while True:
            cur_type = type_manager.get_item_at_index(i)
            if cur_type is GeneralStore.EOF:
                break
            if cur_type is not None:
                type_name = type_name_manager.read_string_at_index(i)
                name_list.append(type_name)
            i += 1

        with timer.paused():
            # Print the resulting name list.
            if not name_list:
                printer.print_info(("No %s found.\n" %
                                    self.show_type.name.lower()), output)
            else:
                printer.print_list(name_list, self.show_type.name,
                    output=output)
