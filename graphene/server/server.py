from antlr4 import InputStream, CommonTokenStream
from graphene.parser import (GQLLexer, GQLParser)
from graphene.commands import *
from graphene.errors.parser_rror import ParserError
from graphene.errors.parser_error_listener import ParserErrorListener
from graphene.storage.storage_manager import StorageManager

class GrapheneServer:
    """
    This class handles execution of commands as the server. It uses the parser
    and dispatches the execution of commands through those classes.
    """
    def __init__(self):
        self.storage_manager = StorageManager()

    def parseCommands(self, commands):
        """
        Parses a list of commands.

        :param list commands: List of commands
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

    def doCommands(self, data):
        """
        Executes a series of commands.

        :param str data: The data coming in from the client or other input
        :return: True if more commands will be accepted, False if an error occurred.
        :rtype: bool
        """

        errorListener = ParserErrorListener()

        # Convert data to input stream
        input = InputStream.InputStream(data)

        # Create lexer and remove error listeners from it
        lexer = GQLLexer(input)
        lexer.removeErrorListeners()

        # Create parser and attach our custom error listener to it
        parser = GQLParser(CommonTokenStream(lexer))
        parser.removeErrorListeners()
        parser.addErrorListener(errorListener)

        # Try to parse the tree. If the parse fails, return False to designate
        # an error. If an error occurs, print it and return True because the
        # error was handled.
        try:
            tree = parser.parse()
            cmds = self.parseCommands(tree.stmt_list().stmts)
            if not cmds:
                return False
            for cmd in cmds:
                cmd.execute(self.storage_manager)
            return True
        except ParserError as e:
            print e
            return True
