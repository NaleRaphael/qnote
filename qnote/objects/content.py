__all__ = ['Content']


class Content(object):
    def __init__(self, value):
        if value is None:
            value = ''
        if not isinstance(value, str):
            raise TypeError('`value` should be a string')
        self.value = value

    def __str__(self):
        return self.value

    def write(self, value):
        self.value = value

    def append(self, value):
        self.value += '\n' + value

    def to_format(self, formatter, **kwargs):
        return formatter(self.value, **kwargs)
