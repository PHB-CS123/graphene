from antlr4 import InputStream, CommonTokenStream
from parser.GQLLexer import GQLLexer
from parser.GQLParser import GQLParser

class GrapheneServer:
    def __init__(self):
        pass

    def parseCommands(self, commands):
        print commands

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
