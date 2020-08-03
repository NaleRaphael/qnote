import os.path as osp
from qnote.config import AppConfig


__all__ = ['HEAD']


class HEAD(object):
    @classmethod
    def _read(cls, fn):
        with open(fn, 'r') as f:
            name = f.read().strip()
        return name

    @classmethod
    def _write(cls, fn, name):
        with open(fn, 'w') as f:
            f.write(name)

    @classmethod
    def get(cls):
        config = AppConfig.load()
        fn_head = config.notebook.fn_head
        name_default = config.notebook.name_default

        if not osp.exists(fn_head):
            cls._write(fn_head, name_default)
            return name_default
        else:
            return cls._read(fn_head)

    @classmethod
    def set(cls, name):
        config = AppConfig.load()
        fn_head = config.notebook.fn_head
        self._write(fn_head, name)
