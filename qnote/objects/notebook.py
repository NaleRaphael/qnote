from datetime import datetime as cls_dt

from .note import Note

__all__ = ['Notebook']


class Notebook(object):
    required_fields = ['name', 'create_time', 'update_time']

    def __init__(self, timestamp, name, notes=None):
        if notes is not None:
            if any([not isinstance(v, Note) for v in notes]):
                raise TypeError('All notes should be %s' % Note)
        else:
            notes = []
        self.name = name
        self.notes = notes
        self._create_time = None
        self._update_time = None
        self.create_time = timestamp
        self.update_time = timestamp

    def __len__(self):
        return len(self.notes)

    def __str__(self):
        ctime = cls_dt.fromtimestamp(self.create_time).strftime('%Y-%m-%d %H:%M:%S')
        utime = cls_dt.fromtimestamp(self.update_time).strftime('%Y-%m-%d %H:%M:%S')
        return '<%s object, created: %s, updated: %s, num_notes: %s>' % (
            self.__class__.__name__, ctime, utime, len(self.notes)
        )

    @property
    def create_time(self):
        return self._create_time

    @create_time.setter
    def create_time(self, value):
        if isinstance(value, cls_dt):
            self._create_time = int(value.timestamp())
        elif isinstance(value, (int, float)):
            self._create_time = int(value)
        else:
            raise TypeError('Unknow type for `create_time`: %s' % type(value))

    @property
    def update_time(self):
        return self._update_time

    @update_time.setter
    def update_time(self, value):
        if isinstance(value, cls_dt):
            self._update_time = int(value.timestamp())
        elif isinstance(value, (int, float)):
            self._update_time = int(value)
        else:
            raise TypeError('Unknow type for `update_time`: %s' % type(value))

    @classmethod
    def create(cls, name):
        create_time = int(cls_dt.now().timestamp())
        return cls(create_time, name)

    @classmethod
    def from_dict(cls, x, load_notes=False):
        checked = [field in x for field in cls.required_fields]
        if not all(checked):
            msg = ', '.join([cls.required_fields[i] for i, v in enumerate(checked) if not v])
            raise ValueError('Missing required field: %s' % msg)

        obj = cls.create(x['name'])
        obj.create_time = x['create_time']
        obj.update_time = x['update_time']

        if load_notes:
            obj.add_notes([Note.from_dict(v) for v in x['notes']])
        return obj

    def to_dict(self):
        return {
            'name': self.name,
            'create_time': self.create_time,
            'update_time': self.update_time,
            'notes': [v.to_dict() for v in self.notes],
        }

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
