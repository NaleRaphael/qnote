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
    required_fields = ['uuid', 'create_time', 'update_time', 'title', 'content', 'tags']

    def __init__(self, uuid, timestamp, title=None, content=None, tags=None):
        if not is_valid_uuid4(uuid):
            raise ValueError('Invalid `uuid`.')
        if not isinstance(timestamp, int):
            try:
                timestamp = int(timestamp)
            except ValueError as ex:
                raise ValueError('Invalid timestamp') from ex
        if tags and not isinstance(tags, Tags):
            raise TypeError('`tags` should be an instance of `%s`' % Tags)
        self.uuid = uuid
        self.create_time = timestamp
        self.update_time = timestamp
        self.title = '' if title is None else title
        self._content = Content(content)
        self.tags = Tags(tags)

    def __str__(self):
        ctime = cls_dt.fromtimestamp(self.create_time).strftime('%Y-%m-%d %H:%M:%S')
        utime = cls_dt.fromtimestamp(self.update_time).strftime('%Y-%m-%d %H:%M:%S')
        str_title = ('%s...' % self.title[:29]) if len(self.title) > 32 else self.title
        return '<%s object, created: %s, updated: %s, title: %s>' % (
            self.__class__.__name__, ctime, utime, str_title
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
    def create(cls, title=None, content=None, tags=None):
        uuid = uuid4()
        create_time = int(cls_dt.now().timestamp())
        return Note(uuid, create_time, title, content, Tags(tags))

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
        obj = cls.create(x['title'], x['content'], tags)

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
            'title': self.title,
            'content': self.content.to_format(str),
            'tags': str(self.tags),
        }

    def update_content(self, raw_content):
        self.content = Content(raw_content)
        self.update_time = int(cls_dt.now().timestamp())
