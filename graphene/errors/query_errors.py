"""
Query custom exceptions.
"""


class NonexistentPropertyException(Exception):
    """Error for accessing or attempting to modify a property that does not
    exist."""
    pass

class TooManyClausesException(Exception):
    """Error for too many ORDER BY, RETURN or LIMIT clauses."""
    pass

class DuplicatePropertyException(Exception):
    """Error for attempting to query with a schema containing duplicate property
    names.."""
    pass

class AmbiguousPropertyException(Exception):
    """Error for attempting to query with a schema containing ambiguous property
    names. That is, a query is created where a property name could refer to more
    than one type in the matching portion of the query, but no specific node
    was designated for that property to refer to."""
    pass

class BadPropertyException(Exception):
    """Error for trying to store the incorrect number of properties in a node or
    relation"""
    pass
