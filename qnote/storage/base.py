__all__ = ['BaseStorer']


class BaseStorer(object):
    def __init__(self, config):
        self.config = config

    def create_note(self, note):
        raise NotImplementedError
