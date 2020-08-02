import os
import os.path as osp
import peewee as pw

from qnote import objects as qo
from qnote.storage.base import BaseStorer

from .models import (
    Note, Notebook, Tag, NoteToNotebook, NoteToTag,
    get_database, proxy,
)


__all__ = ['SQLiteStorer']

STORER_IMPL = 'SQLiteStorer'


class SQLiteStorer(BaseStorer):
    def __init__(self, config):
        super(SQLiteStorer, self).__init__(config)
        self.db = None
        self._initialize_database()

    def _initialize_database(self):
        dir_root = self.config.storage.dir_root
        os.makedirs(dir_root, exist_ok=True)

        storage_path = osp.join(dir_root, 'storage.db')
        self.db = get_database(storage_path)
        proxy.initialize(self.db)
        self.db.create_tables([Note, Notebook, Tag, NoteToNotebook, NoteToTag])

    def create_note(self, note):
        if not isinstance(note, qo.Note):
            raise TypeError('`note` should be an instance of %s' % qo.Note)

        with self.db.atomic() as transaction:
            try:
                pw_note = Note(
                    uuid=str(note._uuid),
                    create_time=note.create_time,
                    update_time=note.update_time,
                    content=note.content.to_format(str),
                )
                pw_note.save()

                for tag in note.tags:
                    # There might be existing tags in database, so we use
                    # `get_or_create()` here
                    pw_tag, _ = Tag.get_or_create(name=str(tag))
                    pw_note2tag = NoteToTag.create(note=pw_note, tag=pw_tag)
            except Exception as ex:
                transaction.rollback()
                raise ex

    def __delete__(self):
        self.db.close()
