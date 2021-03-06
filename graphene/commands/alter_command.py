import sys
from enum import Enum

from graphene.storage import StorageManager
from graphene.commands.command import Command


class AlterCommand(Command):
    class AlterType(Enum):
        DROP_PROPERTY = 1
        ADD_PROPERTY = 2
        CHANGE_PROPERTY = 3
        RENAME_PROPERTY = 4

    def __init__(self, type_name, mods, node_flag):
        self.type_name = type_name
        self.mods = mods
        self.node_flag = node_flag

    def execute(self, storage_manager, output=sys.stdout, timer=None):
        """
        Create the relation specified by this class.
        :type storage_manager: StorageManager
        :param storage_manager: manager that stores the relation to disk
        :return: None
        """
        for mod in self.mods:
            if mod.type == AlterCommand.AlterType.DROP_PROPERTY:
                storage_manager.drop_property(self.type_name, mod.n, self.node_flag)
            elif mod.type == AlterCommand.AlterType.ADD_PROPERTY:
                storage_manager.add_property(self.type_name, mod.n, mod.t, self.node_flag)
            elif mod.type == AlterCommand.AlterType.CHANGE_PROPERTY:
                storage_manager.change_property(self.type_name, mod.n, mod.t, self.node_flag)
            elif mod.type == AlterCommand.AlterType.RENAME_PROPERTY:
                storage_manager.rename_property(self.type_name, mod.n, mod.n2, self.node_flag)
