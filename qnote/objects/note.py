from datetime import datetime as cls_dt
from uuid import UUID, uuid4

from .content import Content
from .tag import Tag, Tags

__all__ = ['Note']


def is_valid_uuid4(x):
    try:
        obj = UUID(x, version=4)
    except ValueError:
        return False
    return str(obj) == x


class Note(object):
    required_fields = ['_uuid', 'timestamp', 'content', 'tags']

    def __init__(self, _uuid, timestamp, content=None, tags=None):
        if not isinstance(_uuid, str):
            raise TypeError('`_uuid` should be a string.')
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
        self.timestamp = timestamp
        self.content = content
        self.tags = tags

    def __str__(self):
        formatted_time = cls_dt.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        val = str(self.content)
        str_content = ('%s...' % val[:29]) if len(val) > 32 else val
        return '<%s object, created: %s, content: %s>' % (
            self.__class__.__name__, formatted_time, str_content
        )

    @classmethod
    def create(cls, raw_content=None, tag_names=None):
        _uuid = str(uuid4())
        timestamp = int(cls_dt.now().timestamp())
        content = Content(raw_content)
        tags = Tags(tag_names)
        return Note(_uuid, timestamp, content, tags)

    @classmethod
    def from_dict(cls, x):
        checked = [field in x for field in cls.required_fields]
        if not all(checked):
            msg = ', '.join([cls.required_fields[i] for i, v in enumerate(checked) if not v])
            raise ValueError('Missing required field: %s' % msg)

        obj = cls.create(x['content'], x['tags'])
        obj._uuid = x['_uuid']
        obj.timestamp = x['timestamp']
        return obj

    def to_dict(self):
        return {
            '_uuid': str(self._uuid),
            'timestamp': self.timestamp,
            'content': self.content.to_format(str),
            'tags': str(self.tags),
        }
