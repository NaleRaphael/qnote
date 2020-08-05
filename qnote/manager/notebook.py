from qnote.internal.exceptions import (
    StorageCheckException,
    StorageRuntimeError
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
        except StorageCheckException:
            raise
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
