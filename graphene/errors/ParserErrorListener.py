from antlr4.error.ErrorListener import ErrorListener
from graphene.errors.ParserError import ParserError

class ParserErrorListener(ErrorListener):

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise ParserError(recognizer, offendingSymbol, line, column, msg, e)
