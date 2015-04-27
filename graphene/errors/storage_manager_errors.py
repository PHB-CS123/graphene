"""
Storage manager custom exceptions.
"""


class TypeAlreadyExistsException(Exception):
    """Error for creating a type that already exists."""
    pass


class TypeDoesNotExistException(Exception):
    """Error for attempting to get type data for a non-existent type."""
    pass
