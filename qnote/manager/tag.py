from qnote.cli.operator import TagOperator
from qnote.internal.exceptions import (
    StorageCheckException,
    SafeExitException,
)
from qnote.objects import Tag, Tags
from qnote.storage import get_storer


__all__ = ['TagManager']


class TagManager(object):
    def __init__(self, config):
        self.config = config

    def list_tags(self):
        storer = get_storer(self.config)
        tags, counts = storer.get_all_tags_with_count()
        lines = ['%4s  %s' % (count, tag) for (count, tag) in zip(counts, tags)]
        msg = '\n'.join(lines)
        print(msg)

    def clear_empty_tags(self):
        """Clear those tags which no notes are tagged by."""
        storer = get_storer(self.config)
        tags, counts = storer.get_all_tags_with_count()
        tags_to_remove = [tags[i] for i, v in enumerate(counts) if v == 0]

        try:
            TagOperator(self.config).confirm_to_remove_tags(tags_to_remove)
        except KeyboardInterrupt as ex:
            raise SafeExitException() from ex

        n_deleted = storer.delete_tags_by_name(tags_to_remove)
        msg = '%s tag%s ha%s been deleted.' % (
            n_deleted,
            's' if n_deleted > 1 else '',
            've' if n_deleted > 1 else 's'
        )
        print(msg)

    def rename_tag(self, old_name, new_name):
        storer = get_storer(self.config)

        if not storer.check_tag_exist(old_name):
            msg = 'Tag "%s" does not exist, so that we cannot rename it' % old_name
            raise SafeExitException(msg)
        if storer.check_tag_exist(new_name):
            msg = 'Tag "%s" already exist, please choose another name' % new_name
            raise SafeExitException(msg)

        storer.rename_tag(old_name, new_name)
        msg = 'Tag "%s" has been renamed "%s"' % (old_name, new_name)
        print(msg)
