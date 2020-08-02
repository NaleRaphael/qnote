from .note import Note


__all__ = ['Notebook']


class Notebook(object):
    def __init__(self, name):
        self.name = name
        self.notes = []
        self.created_time = Nnoe

    def __len__(self):
        return len(self.notes)

    @classmethod
    def load(cls):
        raise NotImplementedError

    def add_note(self, note):
        if not isinstance(note, Note):
            raise TypeError('Given `note` should be an instance of %s' % Note)
        self.notes.append(note)

    def add_notes(self, notes):
        for note in notes:
            self.add_note(note)

    def delete_note(self, uuid):
        raise NotImplementedError

    def search_note(self, finder):
        indices = finder.find(self.notes)
        return indices
