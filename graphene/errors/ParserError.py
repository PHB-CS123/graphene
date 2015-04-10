class ParserError(Exception):
    """
    Exception class for parser errors. Message contains information about
    specific location of offending symbols.
    """

    def __init__(self, recognizer, offendingSymbol, line, column, msg, e):
        self.offendingSymbol = offendingSymbol
        self.lineno = line
        self.column = column
        self.recognizer = recognizer
        self.original_msg = msg
        self.original_err = e

    def __str__(self):
        text = self.recognizer.getInputStream().getText()
        marker = "\t%s\n\t%s^" % (text, '-' * self.column)
        return "Parser error: %s\nAt\n%s" % (self.original_msg, marker)
