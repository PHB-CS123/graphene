"""
Storage manager custom exceptions.
"""


class TypeAlreadyExistsException(Exception):
    """Error for creating a type that already exists."""
    pass

class TypeDoesNotExistException(Exception):
    """Error for attempting to get type data for a non-existent type."""
    pass

class TypeMismatchException(Exception):
    """Error for attempting to store the incorrect data type for a property."""
    pass
