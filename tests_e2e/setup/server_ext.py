from antlr4 import InputStream

from graphene.server.server import GrapheneServer


class GrapheneTestServer(GrapheneServer):
    """
    Server extension class for e2e testing
    """

    def do_test_command(self, data, output):
        """
        Executes a series of commands.

        :param data: The data coming in from the client or other input
        :type data: str
        :return: Nothing
        :rtype: None
        """
        # Convert data to input stream
        istream = InputStream.InputStream(data)

        lexer, parser = self.gen_parser_lexer(istream)

        # Try to parse the tree. If the parse fails, return False to designate
        # an error. If an error occurs, print it and return True because the
        # error was handled.
        tree = parser.parse()
        cmds = self.parseCommands(tree.stmt_list().stmts)
        for cmd in cmds:
            cmd.execute(self.storage_manager, output, timer=self.timer)
