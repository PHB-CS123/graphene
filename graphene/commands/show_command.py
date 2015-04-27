from enum import Enum
from graphene.commands.command import Command
from graphene.utils import PrettyPrinter
from graphene.storage import GeneralStore

class ShowCommand(Command):
    class ShowType(Enum):
        TYPES = 1
        RELATIONS = 2

    def __init__(self, show_type):
        self.show_type = show_type

    def execute(self, storage_manager):
        if self.show_type == ShowCommand.ShowType.TYPES:
            i = 1
            type_list = []
            while True:
                cur_type = storage_manager.type_manager.get_item_at_index(i)
                if cur_type is GeneralStore.EOF:
                    break
                if cur_type is not None:
                    type_name = storage_manager.type_name_manager \
                                .read_name_at_index(cur_type.nameId)
                    type_list.append(type_name)
                i += 1
            if len(type_list) == 0:
                print "No types found."
                return
            PrettyPrinter.print_list(type_list, "Type Name")
