import sys
from antlr4 import *
from GQLLexer import GQLLexer
from GQLParser import GQLParser
from GQLListener import GQLListener

class KeyPrinter(GQLListener):
    def enterMatch_stmt(self, ctx):
        print "Match:"

    def enterNode_chain(self, ctx):
        cnt = ctx.getChildCount()
        for i in range(cnt):
            child = ctx.getChild(i)
            if i % 2 == 0: # even means it's a node
                data = child.node_data
                if data["name"] != None:
                    print "\tNode(%s): %s" % (data["name"], data["type"])
                else:
                    print "\tNode: %s" % data["type"]
            else:
                print "\tRelation: %s" % child.relation_data


def main(argv):
    input = FileStream(argv[1])
    lexer = GQLLexer(input)
    stream = CommonTokenStream(lexer)
    parser = GQLParser(stream)
    tree = parser.parse()
    printer = KeyPrinter()
    walker = ParseTreeWalker()
    walker.walk(printer, tree)

if __name__ == '__main__':
    main(sys.argv)
