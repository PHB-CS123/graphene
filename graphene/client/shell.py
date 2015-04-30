import cmd
import readline
import traceback
import sys
import logging


class Shell(cmd.Cmd):
    def __init__(self, server):
        cmd.Cmd.__init__(self)
        self.server = server

    def preloop(self):
        self.intro = "Graphene 0.1"
        self.prompt = "> "
        self.completekey = "Tab"

    def do_help(self, line):
        """
        Prints help message when the following command is executed:
            > help [line]

        :param line: Line following help command used to identify help request
        :type line: str
        :return: Nothing
        :rtype: None
        """
        # TODO: implement for different types of commands
        # Make the line whitespace and case insensitive
        line = line.upper().strip()

        if line == "MATCH":
            print("MATCH help: ")
        else:
            print("You can type the following help topics: \n"
                  "MATCH, INSERT, CREATE")
            logging.debug("Unhandled help request %s" % line)

    def do_EOF(self, line):
        return True

    def emptyline(self):
        # On empty line, don't do anything at all
        pass

    def format_traceback(self, err_type, err_value, tb):
        full_tb = traceback.extract_tb(tb)
        s = "%s: %s\n%s%s STACK TRACE %s" % (err_type.__name__, err_value,
            " " * len(self.prompt), "=" * 30, "=" * 30)
        for t in full_tb:
            file_name, lineno, fn, line = t
            module_name = file_name.replace("/",".").replace(".py","")
            s += "\n%sIn %s.%s, line %d:\n%s%s" % (" " * len(self.prompt),
                module_name, fn, lineno, " " * (4 + len(self.prompt)), line)
        s += "\n%s%s" % (" " * len(self.prompt), "=" * (2 * 30 + 13))
        return s

    def default(self, line):
        try:
            if not self.server.doCommands(line):
                return True
        except:
            print self.format_traceback(sys.exc_type, sys.exc_value, sys.exc_traceback)
