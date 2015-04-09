from antlr4 import InputStream, CommonTokenStream
from graphene.parser.GQLLexer import GQLLexer
from graphene.parser.GQLParser import GQLParser
from graphene.commands import *

class GrapheneServer:
    def __init__(self):
        pass

    def parseCommands(self, commands):
        for cmd in commands:
            if cmd is None or cmd.c is None:
                # there was an error, so for now ignore it
                # later we will actually say something about it
                continue
            if isinstance(cmd.c.cmd, ExitCommand):
                return False
            print cmd.c.cmd
        return True

    def doCommands(self, data):
        input = InputStream.InputStream(data)
        lexer = GQLLexer(input)
        stream = CommonTokenStream(lexer)
        parser = GQLParser(stream)
        try:
            tree = parser.parse()
            return self.parseCommands(tree.stmt_list().stmts)
        except Exception, e:
            print e
