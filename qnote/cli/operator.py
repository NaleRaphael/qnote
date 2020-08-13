import sys
import re

from qnote.config import AppConfig
from qnote.editor import get_editor
from qnote.objects import Notebook, Note, Tag, Tags
from qnote.internal.exceptions import (
    EditorNotFoundException, EditorNotSupportedException,
    UserCancelledException, SafeExitException,
)
from qnote.utils import (
    query_yes_no, NoteFormatter, show_notes as utils_show_notes
)


__all__ = ['NoteOperator', 'NotebookOperator', 'TagOperator']


note_template = """# Note content (this line can be removed)

"""


class NoteOperator(object):
    def __init__(self, config):
        self.config = config

    def create_note(self):
        # - open editor
        editor = select_editor(self.config)

        try:
            content = editor.open(
                fn_tmp=self.config.editor.fn_tempfile, init_content=note_template
            )
        except UserCancelledException:
            sys.exit(1)

        # No changes in content, nothing to add. Exit the program normally.
        if content == note_template:
            sys.exit(0)

        # - remove template string
        regex = re.compile(re.escape(note_template.strip()))
        content = regex.sub('', content).strip()

        # - parse title
        title = parse_title(content, self.config)

        # - auto parsing tags from note content
        tags, content = parse_tags(content, self.config)

        # - remove leading and trailing spaces again
        content = content.strip()

        try:
            if content == '':
                msg = 'Empty content detected, do you want to save this note?'
                if not query_yes_no(msg, default='no', back_n_lines=1):
                    raise KeyboardInterrupt
        except KeyboardInterrupt:
            print()
            sys.exit(1)

        continue_editing_tags = False
        try:
            print('Tags: %s' % str(tags))
            continue_editing_tags = query_yes_no(
                'Continue editing tags?', default='yes', back_n_lines=1
            )
        except KeyboardInterrupt:
            print()
            sys.exit(1)

        if not continue_editing_tags:
            return Note.create(title, content, tags)

        # - let user edit tags
        try:
            raw_tags = editor.open(
                fn_tmp=self.config.editor.fn_tempfile, init_content=str(tags)
            )
        except UserCancelledException:
            sys.exit(1)

        tags = Tags.from_string_content(raw_tags)
        return Note.create(title, content, tags)

    def edit_note(self, note, editor_name=None):
        from hashlib import md5 as func_md5

        editor = select_editor(self.config, editor_name)

        old_utime = note.update_time
        old_content = note.content.to_format(str)
        hash_old = func_md5(old_content.encode()).hexdigest()

        fn_tmp = self.config.editor.fn_tempfile
        init_content = old_content + '\n'*2 + '^^^%s^^^' % str(note.tags)
        new_content = editor.open(fn_tmp=fn_tmp, init_content=init_content)

        # - parse title
        title = parse_title(new_content, self.config)

        # - auto parsing tags from note content
        tags, new_content = parse_tags(new_content, self.config)

        # - remove leading and trailing spaces again
        new_content = new_content.strip()

        try:
            if new_content == '':
                msg = 'Empty content detected, do you want to save this note?'
                if not query_yes_no(msg, default='no', back_n_lines=1):
                    raise KeyboardInterrupt
        except KeyboardInterrupt:
            print()
            sys.exit(1)

        continue_editing_tags = False
        tags_changed = set(tags) != set(note.tags)
        if tags_changed:
            try:
                msg_tags = str(tags) if len(tags) > 0 else '(no tag)'
                print('Current tags: %s' % msg_tags)
                msg = (
                    'Tags are modified, do you want to edit them? '
                    '(press ctrl+c to abort changes)'
                )
                continue_editing_tags = query_yes_no(msg, default='yes', back_n_lines=1)
            except KeyboardInterrupt:
                print()
                pass

        if continue_editing_tags:
            try:
                raw_tags = editor.open(fn_tmp=fn_tmp, init_content=str(tags))
            except UserCancelledException:
                sys.exit(1)
            try:
                tags = Tags.from_string_content(raw_tags)
                tags_changed = set(tags) != set(note.tags)
            except:
                print('Failed to parse new tags, fallback to orignal ones.')

        hash_new = func_md5(new_content.encode()).hexdigest()
        if hash_old == hash_new and not tags_changed:
            msg = 'Content and tags were not changed.'
            raise SafeExitException(msg)

        note.update_content(new_content)
        note.tags = tags
        return note

    def search_note(self):
        raise NotImplementedError


class NotebookOperator(object):
    def __init__(self, config):
        self.config = config

    def show_notes(self, notes, show_date=False, show_uuid=False):
        tw_config = {
            'witdh': self.config.display.width,
            'max_lines': self.config.display.max_lines,
        }
        utils_show_notes(
            notes, self.config, tw_config, show_date=show_date, show_uuid=show_uuid
        )

    def select_notes(self, notes, multiple=False, show_date=False, show_uuid=False,
        clear_after_exit=False):
        """Interactive mode for selecting note from a list."""
        from qnote.vendor.inquirer import (
            DefaultTheme, ListBoxRender, ListBoxQuestion, prompt
        )

        tw_config = {
            'witdh': self.config.display.width,
            'max_lines': self.config.display.max_lines,
        }
        formatter = NoteFormatter(
            self.config, tw_config=tw_config, show_date=show_date, show_uuid=show_uuid
        )

        # TODO: if `multiple` is True, use `CheckBoxQuestion` instead.
        questions = [
            ListBoxQuestion(
                'selected',
                message='List of notes',
                choices=[(i, v) for i, v in enumerate(notes)]
            )
        ]

        def message_handler(message):
            # NOTE: `message` is a instance of `TaggedValue`, see also
            # https://github.com/magmax/python-inquirer/blob/5412d53/inquirer/questions.py#L111-L117
            return '\n%s\n' % formatter(message.value)

        def choices_searcher(choices, pattern):
            notes = [v.value for v in choices]
            contents = [str(v.content) for v in notes]
            regex = re.compile(re.escape(pattern))
            idx_matched = [i for i, v in enumerate(contents) if regex.search(v) is not None]
            return [choices[i] for i in idx_matched]

        theme = DefaultTheme()
        render_config = {
            'message_handler': message_handler,
            'choices_searcher': choices_searcher,
            'clear_after_exit': clear_after_exit,
        }
        render = ListBoxRender(theme=theme, render_config=render_config)
        try:
            retval = prompt(questions, render=render, raise_keyboard_interrupt=True)
            result = retval['selected']
        except KeyboardInterrupt as ex:
            raise UserCancelledException() from ex

        if result is None:
            return []
        else:
            return result if isinstance(result, list) else [result]

    def confirm_to_clear(self, nb_name):
        msg = (
            'Are you sure you want to delete all notes in this notebook "%s"?' % nb_name
        )
        return query_yes_no(msg, default='no', back_n_lines=1)


class TagOperator(object):
    def __init__(self, config):
        self.config = config

    def confirm_to_remove_tags(self, tags):
        msg_tags = '\n'.join([str(v) for v in tags])
        msg = (
            '%s\nAre you sure you want to remove those tags listed above?' % msg_tags
        )
        return query_yes_no(msg, default='no', back_n_lines=1)


def open_default_editor(fn_tmp='', init_content=''):
    from qnote.vendor.inquirer import (
        DefaultEditorQuestion, ConsoleRender, DefaultTheme, prompt
    )

    questions = [
        DefaultEditorQuestion('content', message=init_content, default_filename=fn_tmp),
    ]
    render = ConsoleRender(theme=DefaultTheme())
    retval = prompt(questions, render=render)
    if retval is None:
        raise UserCancelledException('Operation is cancelled by user.')
    return retval['content']


def select_editor(config, editor_name=None):
    if editor_name is None:
        editor_name = config.editor.executable

    try:
        editor = get_editor(editor_name)
    except (EditorNotFoundException, EditorNotSupportedException) as ex:
        # fallback
        msg = (
            '%s '
            'You can set your favorite one in the config file or use the '
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

        # Create interface `open`
        def wrapper(func):
            func.open = func.__call__
            return func
        editor = wrapper(open_default_editor)

    return editor


def parse_title(content, config):
    # Find the first line as title, which will be truncated if there is too much words.
    return find_title_from_content(content, config.note.max_title_len)


def parse_tags(content, config):
    tags = Tags()

    if config.tag.auto_parse:
        # Extract tags only from those lines enclosed by `^^^`
        # e.g. ^^^#tag1, #tag2^^^
        # So that these line can be removed totally.
        try:
            tags, new_content = extract_tags_from_content(content)
            if config.tag.auto_remove_from_content:
                content = new_content
        except Exception as ex:
            print('Failed to parse tags automatically...')
            input('Press any key to continue')
    return tags, content


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
