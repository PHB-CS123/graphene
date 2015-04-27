import unittest

from antlr4 import InputStream, CommonTokenStream
from graphene.parser.GQLLexer import GQLLexer
from graphene.parser.GQLParser import GQLParser
from graphene.commands import *
from graphene.errors.parser_error import ParserError
from graphene.errors.parser_error_listener import ParserErrorListener

class ParserWrapper:
    def __init__(self):
        self.err_listener = ParserErrorListener()

    def parse(self, data):
        lexer = GQLLexer(InputStream.InputStream(data))
        lexer.removeErrorListeners()
        parser = GQLParser(CommonTokenStream(lexer))
        parser.removeErrorListeners()
        parser.addErrorListener(self.err_listener)

        return parser.parse()

class TestParser(unittest.TestCase):
    def setUp(self):
        self.parser = ParserWrapper()

    def testValidCode(self):
        validStatements = (
                "MATCH (a:A);",
                "MATCH (a:A)-[R]->(b:B);",
                "MATCH (A)-[r:R]->(B);",
                "QUIT;",
                "EXIT;",
                "CREATE TYPE Person ( name : string );",
                "CREATE RELATION R",
                "CREATE RELATION R ( name : string )",
                # case-insensitive identifiers
                "quit",
                "match (a:A)"
            )

        for stmt in validStatements:
            self.assertTrue(self.parser.parse(stmt))

    def testInvalidCode(self):
        invalidStatements = (
                "MATCH;", # missing node chain
                "MATCH (a:A)-[R]->;", # missing end node
                "MATCH (A:A)", # invalid name
                "MATCH (a:a)", # invalid type
                "MATCH (a:A)-[r]->(b:B)", # invalid relation
                "CREATE TYPE Person", # no type list
                "CREATE TYPE PERSON", # invalid identifier for type
            )

        for stmt in invalidStatements:
            self.assertRaises(ParserError, self.parser.parse, stmt)
