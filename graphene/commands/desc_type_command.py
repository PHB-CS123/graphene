from enum import Enum
from graphene.commands.command import Command
from graphene.utils import PrettyPrinter
from graphene.storage import GeneralStore

class DescTypeCommand(Command):
    def __init__(self, type_name):
        self.type_name = type_name

    def execute(self, storage_manager):
        type_data, type_schema = storage_manager.get_node_data(self.type_name)
        values = [(tt_name, tt_type.name) for tt, tt_name, tt_type in type_schema]
        PrettyPrinter.print_table(values, header=("Name", "Type"))
