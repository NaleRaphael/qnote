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

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, x):
        if not isinstance(x, Tag):
            raise TypeError
        return x.name == self.name

    @classmethod
    def is_valid_name(cls, name):
        matched = cls.regex_tag.match(name)
        if matched is None:
            return False
        return matched.group() == name


class Tags(object):
    def __init__(self, tags=None):
        if tags:
            if isinstance(tags, Tags):
                self.collection = tags.collection
            elif all([isinstance(tag, Tag) for tag in tags]):
                self.collection = tags
            elif all([isinstance(tag, str) for tag in tags]):
                self.collection = [Tag(tag) for tag in tags]
            else:
                msg = (
                    '`tags` should be %s or a list of '
                    '{`str` or `%s`}' % (Tags, Tag)
                )
                raise TypeError(msg)
        else:
            self.collection = []

    def __str__(self):
        return ', '.join([str(tag) for tag in self.collection])

    def __len__(self):
        return len(self.collection)

    def __iter__(self):
        return iter(self.collection)

    def __getitem__(self, idx):
        return self.collection[idx]

    def __contains__(self, tag):
        if not isinstance(tag, Tag):
            raise TypeError('`tag` should be a %s' % Tag)
        return str(tag) in set([str(v) for v in self.collection])

    def __add__(self, x):
        if not isinstance(x, (Tag, Tags)):
            raise TypeError('`x` should be %s or %s' % (Tag, Tags))

        result = self.collection
        if isinstance(x, Tag):
            if x not in self:
                result.append(x)
        else:
            result = list(set(result).union(set(x.collection)))
        return Tags(result)

    def __iadd__(self, x):
        if not isinstance(x, (Tag, Tags)):
            raise TypeError('`x` should be %s or %s' % (Tag, Tags))
        if isinstance(x, Tag):
            if x not in self:
                self.collection.append(x)
        else:
            union = set(self.collection).union(set(x.collection))
            self.collection = list(union)
        return self

    def add_tag(self, tag):
        self.__iadd__(tag)

    @classmethod
    def from_string_content(cls, content):
        regex = re.compile(r'(#\w+)')
        result = regex.findall(content)
        return cls(tags=[Tag(v) for v in result])
