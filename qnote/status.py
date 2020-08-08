import os.path as osp
from qnote.config import AppConfig


__all__ = ['HEAD', 'CachedNoteUUIDs']


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
        cls._write(fn_head, name)


class CachedNoteUUIDs(object):
    @classmethod
    def _read(cls, fn):
        with open(fn, 'r') as f:
            uuids = f.readlines()
        return name

    @classmethod
    def _write(cls, fn, uuids):
        with open(fn, 'w') as f:
            f.write(uuids)

    @classmethod
    def get(cls):
        config = AppConfig.load()
        fn = config.fn_cached_note_uuid
        if not osp.exists():
            return []
        else:
            return cls._read(fn)

    @classmethod
    def set(cls, uuids):
        config = AppConfig.load()
        fn = config.fn_cached_note_uuid
        content = '\n'.join([str(v) for v in uuids])
        cls._write(fn, content)
