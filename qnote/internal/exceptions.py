__all__ = [
    'EditorNotFoundError',
    'EditorNotSupportedError',
    'UserCancelledException',
]


class EditorNotFoundError(Exception):
    pass


class EditorNotSupportedError(Exception):
    pass


class UserCancelledException(Exception):
    pass
