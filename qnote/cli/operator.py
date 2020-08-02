import sys
import re

from qnote.config import AppConfig
from qnote.editor import get_editor
from qnote.objects import Notebook, Note, Tag, Tags
from qnote.internal.exceptions import (
    EditorNotFoundError, EditorNotSupportedError, UserCancelledException
)
from qnote.utils import query_yes_no
from qnote.vendor.inquirer import (
    ConsoleRender, DefaultEditor, DefaultEditorQuestion, DefaultTheme
)
from qnote.vendor.inquirer import prompt as inquirer_prompt


__all__ = ['NoteOperator', 'NotebookOperator']


note_template = """# Note content (this line can be removed)

"""


class NoteOperator(object):
    def __init__(self, config):
        self.config = config

    def create_note(self):
        # - open editor
        editor, use_default_editor = None, True

        try:
            editor = get_editor(self.config.editor.executable)
        except (EditorNotFoundError, EditorNotSupportedError) as ex:
            # fallback
            msg = (
                '%s '
                'You can set your favorite one in the config file or use the'
                'default editor and continue editing.\n' % str(ex)
            )
            print(msg)
            try:
                use_default_editor = query_yes_no(
                    'Continue editing?', default='yes', back_n_lines=2
                )
            except KeyboardInterrupt:
                print()
                sys.exit(1)

            if not use_default_editor:
                sys.exit(2)     # no available editors and execution is aborted
            try:
                content = open_default_editor(
                    fn_tmp=self.config.editor.fn_tempfile, init_content=note_template
                )
            except UserCancelledException:
                sys.exit(1)
        else:
            content = editor.open(
                fn_tmp=self.config.editor.fn_tempfile, init_content=note_template
            )

        # No changes in content, nothing to add. Exit the program normally.
        if content == note_template:
            sys.exit(0)

        # - remove template string
        regex = re.compile(re.escape(note_template.strip()))
        content = regex.sub('', content)

        # - auto parsing tags from note content
        if self.config.tag.auto_parse:
            tags = Tags.from_string_content(content)
            if self.config.tag.auto_remove_from_content:
                content = remove_tags_from_string(content, tags)
        else:
            tags = []

        try:
            print('Tags: %s' % str(tags))
            continue_edit_tags = query_yes_no(
                'Continue editing tags?', default='yes', back_n_lines=1
            )
        except KeyboardInterrupt:
            print()
            sys.exit(1)

        if not continue_edit_tags:
            return Note.create(content, tags)

        # - let user edit tags
        if editor is None and use_default_editor:
            try:
                raw_tags = open_default_editor(
                    fn_tmp=self.config.editor.fn_tempfile, init_content=str(tags)
                )
            except UserCancelledException:
                sys.exit(1)
        else:
            raw_tags = editor.open(
                fn_tmp=self.config.editor.fn_tempfile, init_content=str(tags)
            )
        tags = Tags.from_string_content(raw_tags)
        return Note.create(content, tags)

    def edit_note(self, uuid):
        raise NotImplementedError

    def search_note(self):
        raise NotImplementedError


class NotebookOperator(object):
    def __init__(self, config):
        self.config = config

    def create_notebook(self):
        raise NotImplementedError

    def load_notebook(self):
        raise NotImplementedError


def open_default_editor(fn_tmp='', init_content=''):
    questions = [
        DefaultEditorQuestion('content', message=init_content, default_filename=fn_tmp),
    ]
    render = ConsoleRender(theme=DefaultTheme())
    retval = inquirer_prompt(questions, render=render)
    if retval is None:
        raise UserCancelledException('Operation is cancelled by user.')
    return retval['content']


def remove_tags_from_string(string, tags):
    result = string
    for tag in tags:
        regex = re.compile(re.escape(str(tag)))
        result = regex.sub('', result)
    return result
