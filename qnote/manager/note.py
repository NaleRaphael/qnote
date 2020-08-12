from qnote.cli.operator import NoteOperator, NotebookOperator
from qnote.internal.exceptions import (
    UserCancelledException,
    StorageCheckException,
    SafeExitException,
)
from qnote.objects import Note, Tags
from qnote.storage import get_storer
from qnote.status import HEAD, CachedNoteUUIDs
from qnote.utils import show_notes as utils_show_notes


__all__ = ['NoteManager']


class NoteManager(object):
    def __init__(self, config):
        self.config = config

    def create_note(self, raw_title, raw_content, raw_tags):
        nb_name = HEAD.get()
        storer = get_storer(self.config)

        if not storer.check_notebook_exist(nb_name):
            msg = 'Notebook `%s` does not exist' % nb_name
            raise StorageCheckException(msg)

        if raw_content is None:
            note = NoteOperator(self.config).create_note()
        else:
            tags = [] if raw_tags is None else Tags.from_string_content(raw_tags)
            note = Note.create(raw_title, raw_content, tags)

        storer.create_note(note, nb_name)

    def show_note(self, uuid):
        storer = get_storer(self.config)

        if uuid is None:
            # Enter interactive mode and let user select note from current notebook
            nb_name = HEAD.get()
            notes = storer.get_notes_from_notebook(nb_name, n_limit=None)

            try:
                selected_notes = NotebookOperator(self.config).select_notes(
                    notes, multiple=False, show_date=True, show_uuid=True,
                    clear_after_exit=True,
                )

                assert len(selected_notes) == 1
                note = selected_notes[0]
            except UserCancelledException:
                raise SafeExitException()
        else:
            note = storer.get_note(uuid)

        tw_config = {'max_lines': None}     # show all content
        utils_show_notes([note], self.config, tw_config)

    def show_note_from_selected(self):
        storer = get_storer(self.config)
        uuids = CachedNoteUUIDs.get()

        if len(uuids) == 0:
            raise SafeExitException('No selected note.')
        if len(uuids) > 1:
            # TODO: enter interactive mode
            raise NotImplementedError
        else:
            uuid = uuids[0]

        note = storer.get_note(uuid)
        tw_config = {'max_lines': None}     # show all content
        utils_show_notes([note], self.config, tw_config)

    def edit_note(self, uuid, editor_name=None):
        storer = get_storer(self.config)

        if uuid is None:
            # Enter interactive mode and let user select note from current notebook
            nb_name = HEAD.get()
            notes = storer.get_notes_from_notebook(nb_name, n_limit=None)

            try:
                selected_notes = NotebookOperator(self.config).select_notes(
                    notes, multiple=False, show_date=True, show_uuid=True,
                    clear_after_exit=True,
                )

                assert len(selected_notes) == 1
                note = selected_notes[0]
            except UserCancelledException:
                raise SafeExitException()
        else:
            note = storer.get_note(uuid)

        edited_note = NoteOperator(self.config).edit_note(
            note, editor_name=editor_name
        )

        storer.update_note(note)

    def edit_note_from_selected(self, editor_name=None):
        storer = get_storer(self.config)
        uuids = CachedNoteUUIDs.get()

        if len(uuids) == 0:
            raise SafeExitException('No selected note.')
        if len(uuids) > 1:
            # TODO: enter interactive mode
            raise NotImplementedError
        else:
            uuid = uuids[0]

        note = storer.get_note(uuid)
        edited_note = NoteOperator(self.config).edit_note(
            note, editor_name=editor_name
        )

        storer.update_note(note)

    def move_note(self, uuid, nb_name):
        storer = get_storer(self.config)

        if uuid is None:
            # Enter interactive mode and let user select note from current notebook
            current_nb_name = HEAD.get()
            notes = storer.get_notes_from_notebook(current_nb_name, n_limit=None)

            try:
                selected_notes = NotebookOperator(self.config).select_notes(
                    notes, multiple=False, show_date=True, show_uuid=True,
                    clear_after_exit=True,
                )

                assert len(selected_notes) == 1
                note = selected_notes[0]
            except UserCancelledException:
                raise SafeExitException()
        else:
            # Check whether specific note exists
            note = storer.get_note(uuid)

        n_moved = storer.move_note_by_uuid(note.uuid, nb_name)

        msg = '%s note%s ha%s been moved to notebook "%s".' % (
            n_moved,
            's' if n_moved > 1 else '',
            've' if n_moved > 1 else 's',
            nb_name
        )
        print(msg)

    def move_note_from_selected(self, nb_name):
        # TODO: update update_time of notebook
        storer = get_storer(self.config)    # TODO: move this to below
        uuids = CachedNoteUUIDs.get()

        if len(uuids) == 0:
            raise SafeExitException('No selected note.')

        if not storer.check_notebook_exist(nb_name):
            msg = 'Notebook `%s` does not exist' % nb_name
            raise StorageCheckException(msg)

        n_moved = storer.move_note_by_uuid(uuids, nb_name)

        msg = '%s note%s ha%s been moved to notebook "%s".' % (
            n_moved,
            's' if n_moved > 1 else '',
            've' if n_moved > 1 else 's',
            nb_name
        )
        print(msg)

    def remove_note(self, uuid):
        storer = get_storer(self.config)

        if uuid is None:
            # Enter interactive mode and let user select note from current notebook
            nb_name = HEAD.get()
            notes = storer.get_notes_from_notebook(nb_name, n_limit=None)

            try:
                selected_notes = NotebookOperator(self.config).select_notes(
                    notes, multiple=False, show_date=True, show_uuid=True,
                    clear_after_exit=True,
                )

                assert len(selected_notes) == 1
                note = selected_notes[0]
            except UserCancelledException:
                raise SafeExitException()
        else:
            # Check whether specific note exists
            note = storer.get_note(uuid)

        n_removed = storer.remove_note_by_uuid(note.uuid)

        msg = '%s note%s ha%s been removed to trash can.' % (
            n_removed,
            's' if n_removed > 1 else '',
            've' if n_removed > 1 else 's'
        )
        print(msg)

    def remove_note_from_selected(self):
        storer = get_storer(self.config)
        uuids = CachedNoteUUIDs.get()

        if len(uuids) == 0:
            raise SafeExitException('No selected note.')

        n_removed = storer.remove_note_by_uuid(uuids)

        msg = '%s note%s ha%s been removed to trash can.' % (
            n_removed,
            's' if n_removed > 1 else '',
            've' if n_removed > 1 else 's'
        )
        print(msg)
