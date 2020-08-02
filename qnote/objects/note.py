from datetime import datetime as cls_dt
from uuid import UUID, uuid4

from .content import Content
from .tag import Tag, Tags

__all__ = ['Note']


def is_valid_uuid4(x):
    if not isinstance(x, UUID):
        raise TypeError('`x` should be an instance of %s' % UUID)
    return x == UUID(x.hex, version=4)


class Note(object):
    required_fields = ['_uuid', 'create_time', 'update_time', 'content', 'tags']

    def __init__(self, _uuid, timestamp, content=None, tags=None):
        if not is_valid_uuid4(_uuid):
            raise ValueError('Invalid `_uuid`.')
        if not isinstance(timestamp, int):
            try:
                timestamp = int(timestamp)
            except ValueError as ex:
                raise ValueError('Invalid timestamp') from ex
        if content and not isinstance(content, Content):
            raise TypeError('`content` should be an instance of `%s`' % Content)
        if tags and not isinstance(tags, Tags):
            raise TypeError('`tags` should be an instance of `%s`' % Tags)
        self._uuid = _uuid
        self.create_time = timestamp
        self.update_time = timestamp
        self._content = content
        self.tags = tags

    def __str__(self):
        formatted_time = cls_dt.fromtimestamp(self.create_time).strftime('%Y-%m-%d %H:%M:%S')
        val = str(self.content)
        str_content = ('%s...' % val[:29]) if len(val) > 32 else val
        return '<%s object, created: %s, content: %s>' % (
            self.__class__.__name__, formatted_time, str_content
        )

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if not isinstance(value, Content):
            raise TypeError(
                '`value` for updating content should be an instance of %s' % Content
            )
        self.update_time = cls_dt.now().timestamp()
        self._content = value

    @classmethod
    def create(cls, content=None, tags=None):
        _uuid = uuid4()
        create_time = int(cls_dt.now().timestamp())
        content = Content(content)
        return Note(_uuid, create_time, content, Tags(tags))

    @classmethod
    def from_dict(cls, x):
        checked = [field in x for field in cls.required_fields]
        if not all(checked):
            msg = ', '.join([cls.required_fields[i] for i, v in enumerate(checked) if not v])
            raise ValueError('Missing required field: %s' % msg)

        obj = cls.create(x['content'], x['tags'])
        obj._uuid = x['_uuid']
        obj.create_time = x['create_time']
        obj.update_time = x['update_time']
        return obj

    def to_dict(self):
        return {
            '_uuid': self._uuid.hex,
            'create_time': self.create_time,
            'update_time': self.update_time,
            'content': self.content.to_format(str),
            'tags': str(self.tags),
        }
