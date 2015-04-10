from antlr4.error.ErrorListener import ErrorListener
from graphene.errors.ParserError import ParserError

class ParserErrorListener(ErrorListener):

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """
        In the event of a syntax error, we create a ParserError with the
        provided information.
        """
        raise ParserError(recognizer, offendingSymbol, line, column, msg, e)
