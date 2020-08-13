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
