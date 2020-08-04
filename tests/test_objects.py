import pytest

from qnote.objects import Tag, Tags


class TestTag:
    def test_create(self):
        valid_names = [
            '#foo',
            '#bar_buzz',
        ]
        for name in valid_names:
            Tag(name)

        invalid_names = [
            '#space_at_tail ',
            ' #space_at_head',
            '#invalid-char',
            '#mutliple #tag #in #one',
        ]
        for name in invalid_names:
            with pytest.raises(ValueError) as ex:
                Tag(name)

    def test_eq(self):
        tag = Tag('#foo')
        assert tag == Tag('#foo')

    def test_in_set(self):
        tags = [Tag('#foo'), Tag('#bar')]
        tags_set = set(tags)
        assert tags[0] in tags_set
        assert Tag('#foo') in tags_set


class TestTags:
    def test_create(self):
        tags = Tags()
        tags.add_tag(Tag('#abc'))

    def test_eq(self):
        def get_names(_tags):
            return [_tag.name for _tag in _tags]

        tags = Tags()
        tags.add_tag(Tag('#foo'))
        tags.add_tag(Tag('#bar'))
        assert set(get_names(tags)) == set(['#foo', '#bar'])

        tags.add_tag(Tag('#foo'))
        assert len(tags) == 2
        assert set(get_names(tags)) == set(['#foo', '#bar'])

        another_tags = Tags(['#gin', '#fizz', '#bar'])
        tags += another_tags
        assert len(tags) == 4
        assert set(get_names(tags)) == set(['#foo', '#bar', '#gin', '#fizz'])

    def test_in_set(self):
        tags = Tags(['#foo', '#bar'])
        assert Tag('#foo') in tags

        tags = set([Tag('#foo'), Tag('#bar')])
        assert Tag('#foo') in tags
