"""
Query custom exceptions.
"""


class NonexistentPropertyException(Exception):
    """Error for creating a type that already exists."""
    pass


class DuplicatePropertyException(Exception):
    """Error for attempting to get type data for a non-existent type."""
    pass

class AmbiguousPropertyException(Exception):
    """Error for attempting to store the incorrect data type for a property."""
    pass
