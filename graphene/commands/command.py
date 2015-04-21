import abc


class Command(object):
    @abc.abstractmethod
    def __init__(self, ctx):
        raise NotImplementedError

    def __repr__(self):
        return "[Command]"

    def execute(self, storage_manager):
        print "executing..."
