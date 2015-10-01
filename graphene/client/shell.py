from graphene.utils.pretty_printer import *
from graphene.utils.help_docs import HelpDocs
from graphene.errors import query_errors, storage_manager_errors

import cmd
import readline
import traceback
import sys
import logging
import inspect

class Shell(cmd.Cmd):
    user_errors = inspect.getmembers(query_errors, inspect.isclass) + \
              inspect.getmembers(storage_manager_errors, inspect.isclass)
    user_error_types = dict(user_errors).values()

    def __init__(self, server):
        cmd.Cmd.__init__(self)
        self.intro = "Graphene 0.1"
        self.prompt = "> "

        self.server = server
        self.logger = logging.getLogger(self.__class__.__name__)
        # Where help documentation is obtained from
        self.helpDocs = HelpDocs()

    def do_help(self, line):
        """
        Prints help message when the following command is executed:
            > help [line]

        :param line: Line following help command used to identify help request
        :type line: str
        :return: Nothing
        :rtype: None
        """
        # Instance of pretty printer to use for all output
        printer = PrettyPrinter()
        # Make the line whitespace and case insensitive
        line = line.upper().strip()
        # Get possible help topics
        help_topics = self.helpDocs.topics

        if line in help_topics:
            self.helpDocs.print_help_topic(line)
            return
        # User entered invalid help topic
        elif len(line) != 0:
            printer.print_error("ERROR: Unrecognized help topic.")
        # Print possible help topics
        printer.print_help("You ask about the following help topics: \n%s"
                           % "- " + " \n- ".join(help_topics))

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
        # Instance of pretty printer to use for all output
        printer = PrettyPrinter()

        try:
            if not self.server.doCommands(line):
                return True
        except Exception as e:
            # If the error was a user error (i.e. we threw it ourselves because
            # the user inputted a badly formed request), we don't need the stack
            # trace.
            if type(e) not in self.user_error_types:
                trace = self.format_traceback(sys.exc_type, sys.exc_value,
                                                sys.exc_traceback)
                printer.print_error(trace)
            else:
                printer.print_error(e)

