class Command(object):
    def __init__(self, ctx):
        pass

    def __repr__(self):
        return "[Command]"

    def execute(self, storage_manager):
        print "executing..."
