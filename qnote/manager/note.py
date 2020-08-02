from qnote.cli.operator import NoteOperator
from qnote.objects import Note, Tags
from qnote.storage import get_storer


__all__ = ['NoteManager']


class NoteManager(object):
    def __init__(self, config):
        self.config = config

    def create_note(self, raw_content, raw_tags):
        if raw_content is None:
            note = NoteOperator(self.config).create_note()
        else:
            tags = [] if raw_tags is None else Tags.from_string_content(raw_tags)
            note = Note.create(raw_content, tags)

        storer = get_storer(self.config)
        storer.create_note(note)
