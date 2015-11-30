from antlr4 import InputStream, CommonTokenStream
import time
import colorama

from graphene.parser import (GQLLexer, GQLParser)
from graphene.commands.exit_command import *
from graphene.errors.parser_error import ParserError
from graphene.errors.parser_error_listener import ParserErrorListener
from graphene.storage.storage_manager import StorageManager
from graphene.utils.pretty_printer import PrettyPrinter
from graphene.utils.timer import CmdTimer

class GrapheneServer:
    """
    This class handles execution of commands as the server. It uses the parser
    and dispatches the execution of commands through those classes.
    """
    def __init__(self):
        self.storage_manager = StorageManager()
        self.timer = CmdTimer()
        # Initialize color escape sequences whether for Windows or Mac/Linux
        colorama.init()

    def parseString(self, s):
        istream = InputStream.InputStream(s)

        lexer, parser = self.gen_parser_lexer(istream)

        tree = parser.parse()
        return self.parseCommands(tree.stmt_list().stmts)

    def parseCommands(self, commands):
        """
        Parses a list of commands.

        :param commands: List of commands
        :type commands: list
        :rtype: list
        """
        result = []
        for cmd in commands:
            if cmd is None or cmd.c is None:
                # there was an error, so for now ignore it
                # later we will actually say something about it
                continue
            if isinstance(cmd.c.cmd, ExitCommand):
                return False
            command = cmd.c.cmd
            result.append(command)
        return result

    def gen_parser_lexer(self, stream):
        errorListener = ParserErrorListener()

        # Create lexer and remove error listeners from it
        lexer = GQLLexer(stream)
        lexer.removeErrorListeners()

        # Create parser and attach our custom error listener to it
        parser = GQLParser(CommonTokenStream(lexer))
        parser.removeErrorListeners()
        parser.addErrorListener(errorListener)

        return lexer, parser

    def doCommands(self, data, eat_errors=True):
        """
        Executes a series of commands.

        :param str data: The data coming in from the client or other input
        :return: True if more commands will be accepted, False if an error occurred.
        :rtype: bool
        """
        # Instance of pretty printer to use for all output
        printer = PrettyPrinter()

        # Convert data to input stream
        istream = InputStream.InputStream(data)

        lexer, parser = self.gen_parser_lexer(istream)

        # Try to parse the tree. If the parse fails, return False to designate
        # an error. If an error occurs, print it and return True because the
        # error was handled.
        try:
            tree = parser.parse()
            cmds = self.parseCommands(tree.stmt_list().stmts)
            if not cmds:
                return False
            for cmd in cmds:
                self.timer.start()
                cmd.execute(self.storage_manager, timer=self.timer)
                self.timer.stop()
                printer.print_execute_time(0, self.timer.time_elapsed)
            return True
        except ParserError as e:
            if eat_errors:
                printer.print_error(e)
            else:
                raise e
            return True

