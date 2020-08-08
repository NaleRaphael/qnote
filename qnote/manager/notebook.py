import textwrap as tw

from qnote.cli.operator import NotebookOperator
from qnote.internal.exceptions import (
    StorageCheckException,
    StorageRuntimeError,
    SafeExitException,
)
from qnote.storage import get_storer
from qnote.status import HEAD


__all__ = ['NotebookManager']


class NotebookManager(object):
    def __init__(self, config):
        self.config = config

    def show_status(self, name):
        if name is None or name == '':
            nb_name = HEAD.get()
        else:
            nb_name = name

        storer = get_storer(self.config)
        try:
            notebook = storer.get_notebook(nb_name)
        except StorageCheckException as ex_check:
            raise SafeExitException(str(ex_check)) from ex_check
        except Exception as ex:
            raise StorageRuntimeError(str(ex)) from ex

        # Get notebook status
        n_limit = self.config.notebook.status_n_limit
        notes = storer.get_notes_from_notebook(nb_name, n_limit)
        msg_notes = '\n'.join(['  %s' % (str(v)) for v in notes])

        msg_status = (
            'Notebook: %s\n'
            'Created: %s  Updated: %s\n'
            'Recently updated:\n%s' % (
                notebook.name, notebook.create_time, notebook.update_time,
                msg_notes
            )
        )
        print(msg_status)

    def create_notebook(self, name):
        storer = get_storer(self.config)
        notebooks = storer.get_all_notebooks()
        nb_names = [v.name for v in notebooks]

        if name in nb_names:
            msg = 'There is already a notebook called: %s' % name
            raise SafeExitException(msg)

        storer.create_notebook_by_name(name)

    def open_notebook(self, name):
        storer = get_storer(self.config)
        notebooks = storer.get_all_notebooks()
        nb_names = [v.name for v in notebooks]

        if name not in nb_names:
            msg = 'Notebook "%s" does not exist, you have to create it first' % name
            raise SafeExitException(msg)

        HEAD.set(name)

    def list_all_notebooks(self, show_date=None, show_all=False):
        # TODO: mark up opening notebook (HEAD)
        storer = get_storer(self.config)
        notebooks = storer.get_all_notebooks()

        if not show_all:
            excluding_name = [
                self.config.notebook.name_default,
                self.config.notebook.name_trash,
            ]
            notebooks = [v for v in notebooks if v.name not in excluding_name]

        if show_date:
            from datetime import datetime as dt

            fmt_time = '%Y-%m-%d %H:%M:%S'
            time_formatter = lambda x: dt.fromtimestamp(x).strftime(fmt_time)
            formatter = lambda x: '%10s, created: %s, updated: %s' % (
                x.name,
                time_formatter(x.create_time),
                time_formatter(x.update_time),
            )
        else:
            formatter = lambda x: '%s' % x.name

        msg = '\n'.join([formatter(v) for v in notebooks])
        print(msg)

    def rename_notebook(self, old_name, new_name):
        non_editable = [
            self.config.notebook.name_default,
            self.config.notebook.name_trash,
        ]
        if old_name in non_editable:
            msg = 'Cannot rename notebook "%s", it\'s for special purpose.' % name
            raise SafeExitException(msg)

        storer = get_storer(self.config)
        if storer.check_notebook_exist(new_name):
            msg = 'Notebook "%s" already exist, please choose another name' % new_name
            raise SafeExitException(msg)

        storer.rename_notebook(old_name, new_name)

        # If HEAD is pointing to current notebook, set HEAD to new notebook
        if HEAD.get() == old_name:
            HEAD.set(new_name)

    def delete_notebook(self, name, forcibly=False):
        non_deletable = [
            self.config.notebook.name_default,
            self.config.notebook.name_trash,
        ]
        if name in non_deletable:
            msg = 'Cannot delete notebook "%s", it\'s for special purpose.' % name
            raise SafeExitException(msg)

        storer = get_storer(self.config)
        if not storer.check_notebook_exist(name):
            msg = 'Notebook "%s" does not exist' % name
            raise SafeExitException(msg)

        # If there are still notes in a notebook, flag "-f" is required
        notebook = storer.get_notebook_with_notes(name)
        if len(notebook.notes) != 0 and not forcibly:
            msg = (
                'Cannot delete notebook "%s", there are still notes in this '
                'notebook. You can add "-f" flag to force delete it.' % name
            )
            raise SafeExitException(msg)

        # Delete notebook
        storer.delete_notebook(notebook.name)

        # If HEAD is pointing to current notebook, redirect HEAD to [DEFAULTS]
        if HEAD.get() == notebook.name:
            head_default = self.config.notebook.name_default
            HEAD.set(head_default)
            msg = (
                'Redirect to notebook "%s" because "%s" has been deleted but '
                'it was opened.' % (head_default, notebook.name)
            )
            print(msg)

    def show_all_notes(self, show_date=False, show_uuid=False):
        # TODO: functionality of this method is similar to `self.show_status`,
        # maybe we can rewrite this later?
        nb_name = HEAD.get()

        storer = get_storer(self.config)
        if not storer.check_notebook_exist(nb_name):
            msg = (
                'Current HEAD is pointing a notebook which does not exist, '
                'there might be something wrong with HEAD pointer or database.'
            )
            raise SafeExitException(msg)

        notes = storer.get_notes_from_notebook(nb_name, n_limit=None)

        NotebookOperator(self.config).show_notes(
            notes, show_date=show_date, show_uuid=show_uuid
        )
