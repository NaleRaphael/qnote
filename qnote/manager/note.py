from qnote.cli.operator import NoteOperator
from qnote.internal.exceptions import StorageCheckException
from qnote.objects import Note, Tags
from qnote.storage import get_storer
from qnote.status import HEAD


__all__ = ['NoteManager']


class NoteManager(object):
    def __init__(self, config):
        self.config = config

    def create_note(self, raw_content, raw_tags):
        nb_name = HEAD.get()
        storer = get_storer(self.config)

        if not storer.check_notebook_exist(nb_name):
            msg = 'Notebook `%s` does not exist' % nb_name
            raise StorageCheckException(msg)

        if raw_content is None:
            note = NoteOperator(self.config).create_note()
        else:
            tags = [] if raw_tags is None else Tags.from_string_content(raw_tags)
            note = Note.create(raw_content, tags)

        storer.create_note(note, nb_name)
