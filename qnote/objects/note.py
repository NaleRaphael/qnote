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
    required_fields = ['uuid', 'create_time', 'update_time', 'content', 'tags']

    def __init__(self, uuid, timestamp, content=None, tags=None):
        if not is_valid_uuid4(uuid):
            raise ValueError('Invalid `uuid`.')
        if not isinstance(timestamp, int):
            try:
                timestamp = int(timestamp)
            except ValueError as ex:
                raise ValueError('Invalid timestamp') from ex
        if content and not isinstance(content, Content):
            raise TypeError('`content` should be an instance of `%s`' % Content)
        if tags and not isinstance(tags, Tags):
            raise TypeError('`tags` should be an instance of `%s`' % Tags)
        self.uuid = uuid
        self.create_time = timestamp
        self.update_time = timestamp
        self._content = content
        self.tags = tags

    def __str__(self):
        ctime = cls_dt.fromtimestamp(self.create_time).strftime('%Y-%m-%d %H:%M:%S')
        utime = cls_dt.fromtimestamp(self.update_time).strftime('%Y-%m-%d %H:%M:%S')
        val = str(self.content)
        str_content = ('%s...' % val[:29]) if len(val) > 32 else val
        return '<%s object, created: %s, updated: %s, content: %s>' % (
            self.__class__.__name__, ctime, utime, str_content
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
        uuid = uuid4()
        create_time = int(cls_dt.now().timestamp())
        content = Content(content)
        return Note(uuid, create_time, content, Tags(tags))

    @classmethod
    def from_dict(cls, x):
        checked = [field in x for field in cls.required_fields]
        if not all(checked):
            msg = ', '.join([cls.required_fields[i] for i, v in enumerate(checked) if not v])
            raise ValueError('Missing required field: %s' % msg)

        raw_tags = x['tags']
        if isinstance(raw_tags, str):
            tags = Tags.from_string_content(raw_tags)
        else:
            tags = Tags(raw_tags)
        obj = cls.create(x['content'], tags)

        obj.uuid = x['uuid']
        for attr_name in ['create_time', 'update_time']:
            if isinstance(x[attr_name], cls_dt):
                setattr(obj, attr_name, int(x[attr_name].timestamp()))
            elif isinstance(x[attr_name], int):
                setattr(obj, attr_name, x[attr_name])
            else:
                raise TypeError('Invalid type of %s' % attr_name)
        return obj

    def to_dict(self):
        return {
            'uuid': self.uuid.hex,
            'create_time': self.create_time,
            'update_time': self.update_time,
            'content': self.content.to_format(str),
            'tags': str(self.tags),
        }
