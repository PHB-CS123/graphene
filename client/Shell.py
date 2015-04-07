import cmd

class Shell(cmd.Cmd):
    def __init__(self, server):
        cmd.Cmd.__init__(self)
        self.server = server

    def preloop(self):
        self.intro = "Graphene 0.1"
        self.prompt = "> "
        self.completekey = "Tab"

    def do_help(self, line):
        # Help message.
        # TODO: Actually be helpful
        pass

    def do_EOF(self, line):
        return True

    def emptyline(self):
        # On empty line, don't do anything at all
        pass

    def default(self, line):
        try:
            self.server.doCommands(line)
        except Exception, e:
            print "Error: %s" % e
