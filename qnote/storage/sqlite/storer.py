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
            # Explicitly checking by this query instead of calling
            # `self.create_notebook(name, exist_ok=True)` to avoid
            # confusion and unnecessary overhead of function call.
            if not self.check_notebook_exist(name):
                notebook = qo.Notebook.create(name)
                self.create_notebook(notebook)

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
                    title=note.title,
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

    def get_note(self, note_uuid):
        query = (
            Note
            .select(Note, pw.fn.group_concat(Tag.name).alias('tags'))
            .where(Note.uuid == note_uuid)
            .join(NoteToTag)
            .join(Tag)
            .group_by(Note.uuid)
        )
        result = list(query.namedtuples())

        if len(result) == 0:
            msg = 'Failed to find note with UUID: %s' % note_uuid
            raise StorageExecutionException(msg)

        if len(result) > 1:
            msg = 'Duplicate notes found.'
            raise StorageExecutionException(msg)

        return qo.Note.from_dict(result[0]._asdict())

    def update_note(self, note):
        if not isinstance(note, qo.Note):
            raise TypeError('`note` should be an instance of %s' % qo.Note)

        data = note.to_dict()

        # pop out those fields should not be updated
        data.pop('uuid')
        data.pop('create_time')
        data.pop('tags')
        data_to_update = {getattr(Note, k): v for k, v in data.items()}

        with self.db.atomic() as transaction:
            try:
                pw_ori_note = list(Note.select().where(Note.uuid == note.uuid))
                if len(pw_ori_note) > 1:
                    raise StorageExecutionException('Duplicate records.')
                if len(pw_ori_note) == 0:
                    raise StorageExecutionException('Record not found: %s' % note.uuid)
                pw_ori_note = pw_ori_note[0]

                query = (
                    Note
                    .update(data_to_update)
                    .where(Note.uuid == note.uuid)
                )
                n_updated = query.execute()

                # sanity check
                if n_updated > 1:
                    raise StorageExecutionException('Duplicate records.')
                if n_updated == 0:
                    raise StorageExecutionException('No record got updated.')

                # add new tags and delete removed tags
                pw_ori_tags = list(
                    Tag
                    .select()
                    .join(NoteToTag)
                    .where(NoteToTag.note_id == pw_ori_note.id)
                )
                ori_tags = qo.Tags([v.name for v in pw_ori_tags])

                tags_to_add = list(set(note.tags) - set(ori_tags))
                tags_to_delete = list(set(ori_tags) - set(note.tags))

                if len(tags_to_add) != 0:
                    tag_names = [str(v) for v in tags_to_add]
                    pw_tags_to_add = list(Tag.select().where(Tag.name.in_(tag_names)))
                    for v in tag_names:
                        pw_tag, _ = Tag.get_or_create(name=str(v))
                        pw_note2tag = NoteToTag.create(note=pw_ori_note, tag=pw_tag)

                if len(tags_to_delete) != 0:
                    tag_names = [str(v) for v in tags_to_delete]
                    pw_tags_to_delete = list(Tag.select().where(Tag.name.in_(tag_names)))
                    query_delete_tags = NoteToTag.delete().where(
                        (NoteToTag.note_id == pw_ori_note.id) &
                        (NoteToTag.tag_id.in_([v.id for v in pw_tags_to_delete]))
                    ).execute()
            except Exception as ex:
                transaction.rollback()
                raise StorageExecutionException(str(ex)) from ex

    def delete_note(self, note, nb_name):
        raise NotImplementedError

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
                pw_notebook, not_existed = Notebook.get_or_create(
                    name=notebook.name, defaults={
                        'create_time': notebook.create_time,
                        'update_time': notebook.update_time
                    }
                )
                if not exist_ok and not not_existed:
                    msg = 'Notebook `%s` already exists.' % notebook.name
                    raise StorageCheckException(msg)
            except StorageCheckException:
                raise
            except Exception as ex:
                transaction.rollback()
                raise StorageExecutionException(str(ex)) from ex

    def create_notebook_by_name(self, nb_name):
        notebook = qo.Notebook.create(nb_name)
        self.create_notebook(notebook, exist_ok=False)

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

    def get_all_notebooks(self):
        query = Notebook.select()
        result = list(query.namedtuples())
        return [qo.Notebook.from_dict(v._asdict()) for v in result]

    def get_notebook_with_notes(self, nb_name, n_limit=None, order='descending'):
        notebook = self.get_notebook(nb_name)
        notes = self.get_notes_from_notebook(nb_name, n_limit=n_limit, order=order)
        notebook.add_notes(notes)
        return notebook

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
            .join(NoteToTag, join_type=pw.JOIN.LEFT_OUTER, on=(Note.id == NoteToTag.note_id))
            .join(Tag, join_type=pw.JOIN.LEFT_OUTER)
            .group_by(Note.uuid)
            .namedtuples()
        )
        result = [v for v in query]
        notes = [qo.Note.from_dict(v._asdict()) for v in query]
        return notes

    def rename_notebook(self, old_name, new_name):
        with self.db.atomic() as transaction:
            try:
                query = (
                    Notebook
                    .update({Notebook.name: new_name})
                    .where(Notebook.name == old_name)
                )
                query.execute()
            except Exception as ex:
                transaction.rollback()
                raise StorageExecutionException(str(ex)) from ex

    def clear_notebook(self, nb_name):
        with self.db.atomic() as transaction:
            try:
                pw_trash_can = list(Notebook.select().where(Notebook.name == nb_name))
                trash_can_id = pw_trash_can[0].id

                pw_notes = list(
                    Note
                    .select()
                    .join(NoteToNotebook)
                    .where(NoteToNotebook.notebook_id == trash_can_id)
                )
                NoteToTag.delete().where(
                    NoteToTag.note_id.in_(pw_notes)
                ).execute()
                q_del_notebook = NoteToNotebook.delete().where(
                    NoteToNotebook.notebook_id == trash_can_id
                )
                assert q_del_notebook.execute() == len(pw_notes)
                q_del_notes = Note.delete().where(
                    Note.id.in_(pw_notes)
                )
                assert q_del_notes.execute() == len(pw_notes)
            except Exception as ex:
                transaction.rollback()
                raise StorageExecutionException(str(ex)) from ex
        return len(pw_notes)

    def delete_notebook(self, nb_name):
        query = (
            Note
            .select()
            .join(NoteToNotebook)
            .join(Notebook)
            .where(Notebook.name == nb_name)
        )

        result = list(query)
        if len(result) != 0:
            self._delete_notebook_containing_notes(nb_name)
        else:
            self._delete_empty_notebook(nb_name)

    def _delete_notebook_containing_notes(self, nb_name):
        with self.db.atomic() as transaction:
            try:
                query_notes = (
                    Note
                    .select()
                    .join(NoteToNotebook)
                    .join(Notebook)
                    .where(Notebook.name == nb_name)
                )

                # NOTE: We have to execute this query before deleting rows in
                # `NoteToNotebook`. Otherwise, result of this query will become
                # empty after those relations in `NoteToNotebook` are deleted.
                # And that will make it failed to delete notes.
                note_ids = [v.id for v in query_notes]

                # Delete relations
                NoteToTag.delete().where(
                    NoteToTag.note_id.in_(query_notes)
                ).execute()
                NoteToNotebook.delete().where(
                    NoteToNotebook.note_id.in_(query_notes)
                ).execute()

                # Delete notes and notebook
                Note.delete().where(Note.id.in_(note_ids)).execute()
                Notebook.delete().where(Notebook.name == nb_name).execute()
            except Exception as ex:
                transaction.rollback()
                raise StorageExecutionException(str(ex)) from ex

    def _delete_empty_notebook(self, nb_name):
        with self.db.atomic() as transaction:
            try:
                Notebook.delete().where(Notebook.name == nb_name).execute()
            except Exception as ex:
                transaction.rollback()
                raise StorageExecutionException(str(ex)) from ex
