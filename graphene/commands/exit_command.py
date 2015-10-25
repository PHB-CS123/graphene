import sys

from graphene.commands.command import Command

class ExitCommand(Command):
    def __init__(self):
        pass

    def execute(self, storage_manager, output=sys.stdout, timer=None):
        # This should never be used anyway.
        pass
