class ParserError(Exception):
    def __init__(self, message):
        super(ParserError, self).__init__(message)
