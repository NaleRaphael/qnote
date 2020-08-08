import sys
import re

from qnote.config import AppConfig
from qnote.editor import get_editor
from qnote.objects import Notebook, Note, Tag, Tags
from qnote.internal.exceptions import (
    EditorNotFoundException, EditorNotSupportedException,
    UserCancelledException
)
from qnote.utils import query_yes_no, NoteFormatter
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
        except (EditorNotFoundException, EditorNotSupportedException) as ex:
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
        content = regex.sub('', content).strip()

        # - parse title (the first line starts with "#*")
        title = find_title_from_content(content, self.config.note.max_title_len)

        # - auto parsing tags from note content
        tags = Tags()
        if self.config.tag.auto_parse:
            # Extract tags only from those lines enclosed by `^^^`
            # e.g. ^^^#tag1, #tag2^^^
            # So that these line can be removed totally.
            try:
                tags, new_content = extract_tags_from_content(content)
                if self.config.tag.auto_remove_from_content:
                    content = new_content
            except Exception as ex:
                print('Failed to parse tags automatically...')
                input('Press any key to continue')

        # - remove leading and trailing spaces again
        content = content.strip()

        try:
            print('Tags: %s' % str(tags))
            continue_edit_tags = query_yes_no(
                'Continue editing tags?', default='yes', back_n_lines=1
            )
        except KeyboardInterrupt:
            print()
            sys.exit(1)

        if not continue_edit_tags:
            return Note.create(title, content, tags)

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
        return Note.create(title, content, tags)

    def edit_note(self, uuid):
        # TODO: update `note.update_time`
        raise NotImplementedError

    def search_note(self):
        raise NotImplementedError


class NotebookOperator(object):
    def __init__(self, config):
        self.config = config

    def show_notes(self, notes, show_date=False, show_uuid=False):
        from shutil import which

        # 3: title, tags, content; 2: newlines for spacing
        n_lines = len(notes) * (
            3 + int(show_date) + int(show_uuid) + self.config.display.max_lines + 2
        )
        pager = self.config.display.pager
        use_pager = False

        # Check whether pager is necessary to use
        # TODO: maybe we can detect current terminal height for this
        if which(pager) is not None and n_lines > 50:
            import os, pydoc

            use_pager = True
            if os.getenv('PAGER', None) is None:
                os.environ['PAGER'] = pager

        # Prepare formatter
        tw_config = {
            'witdh': self.config.display.width,
            'max_lines': self.config.display.max_lines,
        }
        formatter = NoteFormatter(
            self.config, tw_config=tw_config, show_date=show_date, show_uuid=show_uuid
        )

        # Print notes
        output = ''
        for note in notes:
            output += '\n%s\n' % formatter(note)

        if use_pager:
            pydoc.pager(output)
        else:
            print(output)


def open_default_editor(fn_tmp='', init_content=''):
    questions = [
        DefaultEditorQuestion('content', message=init_content, default_filename=fn_tmp),
    ]
    render = ConsoleRender(theme=DefaultTheme())
    retval = inquirer_prompt(questions, render=render)
    if retval is None:
        raise UserCancelledException('Operation is cancelled by user.')
    return retval['content']


def extract_tags_from_content(content):
    all_tags = Tags()
    new_content = content

    # NOTE: Here we don't make this pattern to recognize leading spaces.
    #   This makes users able to avoid auto-parsing those lines
    #   (Just like the way how `git` handles comment lines)
    matches = re.compile(r'\^{3}\s*(#\w+[,\s]*)+\^{3}[\s\n]*').finditer(content)
    for line in matches:
        all_tags += Tags.from_string_content(line.group())
        new_content = new_content.replace(line.group(), '')

    return all_tags, new_content


def find_title_from_content(content, max_title_len):
    title = ''
    content += '\n'
    idx_title_end = content.find('\n')

    if idx_title_end == -1:
        return title

    # find the last space to avoid breaking words
    if idx_title_end > max_title_len:
        idx_last_space = content[:idx_title_end].rfind(' ')
        # in case the first line is a string without spaces
        if idx_last_space != -1:
            idx_title_end = idx_last_space

    title = content[:idx_title_end].strip()
    return title
