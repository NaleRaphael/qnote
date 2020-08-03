"""Custom defined exception classes.

Note that classes with suffix `Exception` should be tried to caught and
handled properly.
"""

__all__ = [
    'EditorNotFoundException',
    'EditorNotSupportedException',
    'UserCancelledException',
    'StorageCheckException',
    'StorageExecutionException',
    'StorageRuntimeError',
]


class EditorNotFoundException(Exception):
    pass


class EditorNotSupportedException(Exception):
    pass


class UserCancelledException(Exception):
    """Exceptions related to those operations cancelled by users in
    interactive mode."""
    pass


class StorageCheckException(Exception):
    """Exceptions related to failure of performing checks on storage.
    e.g. checking whether a table exists, raise this exception to terminate
    execution."""
    pass


class StorageExecutionException(Exception):
    """Exceptions related to failure of operating storage."""
    pass


class StorageRuntimeError(RuntimeError):
    """Just like the meaning of built-in `RuntimeError`, those exceptions
    which got detected but not able to be classified to other categories
    should be raised in this type."""
    pass
