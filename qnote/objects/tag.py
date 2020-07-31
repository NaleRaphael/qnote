import re

__all__ = ['Tag', 'Tags']


class Tag(object):
    regex_tag = re.compile(r'^#(\w+)')

    def __init__(self, name):
        if not self.is_valid_name(name):
            raise ValueError('Invalid name')
        self.name = name

    def __str__(self):
        return '%s' % self.name

    @classmethod
    def is_valid_name(cls, name):
        matched = cls.regex_tag.match(name)
        if matched is None:
            return False
        return matched.group() == name


class Tags(object):
    def __init__(self, tags=None):
        if tags:
            if all([isinstance(tag, Tag) for tag in tags]):
                self.collection = tags
            elif all([isinstance(tag, str) for tag in tags]):
                self.collection = [Tag(tag) for tag in tags]
            else:
                raise TypeError('`tags` should be a list of `str` or %s' % Tag)
        else:
            self.collection = []

    def __str__(self):
        return ', '.join([str(tag) for tag in self.collection])

    def __iter__(self):
        return iter(self.collection)

    def add(self, name):
        self.collection.append(Tag(name))

    def add_tag(self, tag):
        if not isinstance(tag, Tag):
            raise TypeError('`tag` should be an instance of %s' % Tag)
        self.collection.append(tag)

    @classmethod
    def from_string_content(cls, content):
        regex = re.compile(r'(#\w+)')
        result = regex.findall(content)
        return cls(tags=[Tag(v) for v in result])
