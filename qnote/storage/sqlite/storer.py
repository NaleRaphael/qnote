import os
import os.path as osp
import peewee as pw

from qnote import objects as qo
from qnote.storage.base import BaseStorer
from qnote.internal.exceptions import (
    StorageCheckException,
    StorageExecutionException,
    StorageRuntimeError,
)

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

    def __delete__(self):
        self.db.close()

    def _initialize_database(self):
        dir_root = self.config.storage.dir_root
        os.makedirs(dir_root, exist_ok=True)

        storage_path = osp.join(dir_root, 'storage.db')
        self.db = get_database(storage_path)
        proxy.initialize(self.db)
        self.db.create_tables([Note, Notebook, Tag, NoteToNotebook, NoteToTag])

        self._initialize_tables()

    def _initialize_tables(self):
        nb_names = [
            self.config.notebook.name_default,
            self.config.notebook.name_trash
        ]
        for name in nb_names:
            notebook = qo.Notebook.create(name)
            self.create_notebook(notebook, exist_ok=True)

    def _query_get_notebook(self, nb_name):
        """Query of `get_notebook()` operation."""
        return Notebook.select().where(Notebook.name == nb_name)

    def create_note(self, note, nb_name):
        if not isinstance(note, qo.Note):
            raise TypeError('`note` should be an instance of %s' % qo.Note)

        with self.db.atomic() as transaction:
            try:
                # Insert note to table
                pw_note = Note(
                    uuid=str(note.uuid),
                    create_time=note.create_time,
                    update_time=note.update_time,
                    content=note.content.to_format(str),
                )
                pw_note.save()

                # Insert tag and relation of "note-tag" to tables
                for tag in note.tags:
                    # There might be existing tags in database, so we use
                    # `get_or_create()` here
                    pw_tag, _ = Tag.get_or_create(name=str(tag))
                    pw_note2tag = NoteToTag.create(note=pw_note, tag=pw_tag)

                # Insert relation "note-notebook" to table
                pw_notebook = list(self._query_get_notebook(nb_name))[0]
                pw_note2notebook = NoteToNotebook.create(
                    note=pw_note, notebook=pw_notebook
                )
            except Exception as ex:
                transaction.rollback()
                raise StorageExecutionException(str(ex)) from ex

    def check_notebook_exist(self, nb_name):
        """
        Parameters
        ----------
        nb_name : str
            Name of notebook to check.

        Returns
        -------
        exist : bool
        """
        return self._query_get_notebook(nb_name).exists()

    def create_notebook(self, notebook, exist_ok=False):
        """
        Parameters
        ----------
        notebook : qnote.objects.Notebook
        exist_ok : bool
            If false, `StorageCheckException` will be raised if notebook
            already exists.
        """
        with self.db.atomic() as transaction:
            try:
                pw_notebook, exists = Notebook.get_or_create(
                    name=notebook.name, defaults={
                        'create_time': notebook.create_time,
                        'update_time': notebook.update_time
                    }
                )
                if not exist_ok and exists:
                    msg = 'Notebook `%s` already exists.' % notebook.name
                    raise StorageCheckException(msg)
            except StorageCheckException:
                raise
            except Exception as ex:
                transaction.rollback()
                raise StorageExecutionException(str(ex)) from ex

    def get_notebook(self, nb_name):
        """
        Parameters
        ----------
        nb_name : str
            Name of notebook.

        Returns
        -------
        notebook : qnote.objects.Notebook
        """
        query = self._query_get_notebook(nb_name)
        if not query.exists():
            raise StorageCheckException('Notebook `%s` does not exist' % nb_name)

        result = list(query.namedtuples())
        assert len(result) == 1

        return qo.Notebook.from_dict(result[0]._asdict())

    def get_notes_from_notebook(self, nb_name, n_limit=None, order='descending'):
        order_converter = {
            'ascending': lambda x: x,
            'descending': lambda x: -x,
        }

        if order.lower() not in order_converter:
            msg = '`order` should be one of %s' % list(order_converter.keys())
            raise ValueError(msg)

        query = (
            Note
            .select()
            .join(NoteToNotebook)
            .join(Notebook)
            .where(Notebook.name == nb_name)
            .order_by(order_converter[order](Note.update_time))
            .limit(n_limit)
            .select(Note, pw.fn.group_concat(Tag.name).alias('tags'))
            .join(NoteToTag, on=(Note.id == NoteToTag.note_id))
            .join(Tag)
            .group_by(Note.uuid)
            .namedtuples()
        )
        result = [v for v in query]
        notes = [qo.Note.from_dict(v._asdict()) for v in query]
        return notes
