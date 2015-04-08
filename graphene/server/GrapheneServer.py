from antlr4 import InputStream, CommonTokenStream
from graphene.parser.GQLLexer import GQLLexer
from graphene.parser.GQLParser import GQLParser

class GrapheneServer:
    def __init__(self):
        pass

    def parseCommands(self, commands):
        for cmd in commands:
            if cmd is None or cmd.c is None:
                # there was an error, so for now ignore it
                # later we will actually say something about it
                continue
            print cmd.c.cmd

    def doCommands(self, data):
        input = InputStream.InputStream(data)
        lexer = GQLLexer(input)
        stream = CommonTokenStream(lexer)
        parser = GQLParser(stream)
        try:
            tree = parser.parse()
            self.parseCommands(tree.stmt_list().stmts)
        except Exception, e:
            print e
