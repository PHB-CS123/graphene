"""
Query custom exceptions.
"""


class NonexistentPropertyException(Exception):
    """Error for creating a type that already exists."""
    pass

class TooManyClausesException(Exception):
    """Error for too many ORDER BY, RETURN or LIMIT clauses."""
    pass

class DuplicatePropertyException(Exception):
    """Error for attempting to get type data for a non-existent type."""
    pass

class AmbiguousPropertyException(Exception):
    """Error for attempting to store the incorrect data type for a property."""
    pass

class BadPropertyException(Exception):
    """Error for trying to store the incorrect number of properties in a node or
    relation"""
    pass
