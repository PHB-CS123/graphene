from antlr4 import InputStream, CommonTokenStream
from graphene.parser.GQLLexer import GQLLexer
from graphene.parser.GQLParser import GQLParser
from graphene.commands import *
from graphene.errors.ParserError import ParserError
from graphene.errors.ParserErrorListener import ParserErrorListener

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
        errorListener = ParserErrorListener();
        input = InputStream.InputStream(data)
        lexer = GQLLexer(input)
        lexer.removeErrorListeners()
        stream = CommonTokenStream(lexer)
        parser = GQLParser(stream)
        parser.removeErrorListeners()
        parser.addErrorListener(errorListener)
        try:
            tree = parser.parse()
            return self.parseCommands(tree.stmt_list().stmts)
        except ParserError as e:
            print "Parser error: %s" % e
            return True
