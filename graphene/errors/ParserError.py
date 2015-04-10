class ParserError(Exception):
    def __init__(self, recognizer, offendingSymbol, line, column, msg, e):
        self.offendingSymbol = offendingSymbol
        self.lineno = line
        self.column = column
        self.recognizer = recognizer
        self.original_msg = msg
        self.original_err = e

    def __str__(self):
        print dir(self.offendingSymbol.getTokenSource())
        return self.original_msg
