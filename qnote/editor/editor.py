import errno, os, tempfile
from subprocess import call
from shutil import which

from qnote.internal.exceptions import (
    EditorNotFoundException, EditorNotSupportedException
)


__all__ = ['get_editor']


def get_editor(name):
    from qnote.editor import editor as this_mod

    editor_names = [name for name in dir(this_mod) if name.endswith('Editor')]
    lower_names = [name.lower() for name in editor_names]
    try:
        idx = lower_names.index('%seditor' % name.lower())
    except ValueError as ex:
        raise EditorNotSupportedException('Editor `%s` is not supported.' % name) from ex

    cls_editor = getattr(this_mod, editor_names[idx])
    return cls_editor()


class EditorBase(object):
    executable = ''

    def __init__(self):
        assert hasattr(self, 'executable'), (
            'Attribute `executable` has not been implemented in this class.'
        )
        self.fn_executable = which(self.executable)
        if self.fn_executable is None:
            raise EditorNotFoundException(
                'Executable of editor `%s` is not found in this system.'
                % self.executable
            )

    def open(self, fn_tmp='', init_content=''):
        # Modified solution from https://stackoverflow.com/a/6309753
        # We have to release the file handler before opening it with editor

        if fn_tmp == '' or fn_tmp is None:
            tf = tempfile.NamedTemporaryFile(suffix='.tmp', delete=False)
            fn_temp = tf.name
        else:
            tf = open(fn_tmp, 'ab')

        tf.write(init_content.encode())   # byte string is required
        tf.close()

        # Call editor and wait for editing
        self.call_editor(fn_tmp)

        # Now control 
        tf = open(fn_tmp, 'r')
        content = tf.read()
        tf.close()

        try:
            os.remove(fn_tmp)
        except OSError as ex:
            if ex.errno != errno.ENOENT:
                # re-raise exception if catched error message is not
                # "no such file or directory"
                raise
        return content

    def call_editor(self, fn):
        call([self.fn_executable, fn])


class VimEditor(EditorBase):
    executable = 'vim'

    def __init__(self):
        super(VimEditor, self).__init__()


class NanoEditor(EditorBase):
    executable = 'nano'

    def __init__(self):
        super(NanoEditor, self).__init__()


class NotepadEditor(EditorBase):
    executable = 'notepad'

    def __init__(self):
        super(NotepadEditor, self).__init__()


class VSCodeEditor(EditorBase):
    executable = 'code'

    def __init__(self):
        super(VSCodeEditor, self).__init__()

    def call_editor(self, fn):
        # See also:
        # https://code.visualstudio.com/docs/editor/command-line#_core-cli-options
        # `--wait`: Wait for the files to be closed before returning.
        call([self.fn_executable, fn, '--wait'])
