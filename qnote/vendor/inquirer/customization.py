from collections import namedtuple
from readchar import key
import editor   # python-editor, a dependency of python-inquirer
from inquirer import errors
from inquirer.render.console import Editor as _EditorRender
from inquirer.render.console import ConsoleRender as _ConsoleRender
from inquirer.render.console import (
    Text, Editor, Password, Confirm, List, Checkbox, Path
)
from inquirer.themes import Default as _DefaultTheme
from inquirer.themes import term as _term
from inquirer.questions import Question as _EditorQuestion


__all__ = [
    'ConsoleRender', 'DefaultEditor', 'DefaultEditorQuestion', 'DefaultTheme',
]


class ConsoleRender(_ConsoleRender):
    def render_factory(self, question_type):
        matrix = {
            'text': Text,
            'editor': Editor,
            'default_editor': DefaultEditor,    # added by us
            'password': Password,
            'confirm': Confirm,
            'list': List,
            'checkbox': Checkbox,
            'path': Path,
        }

        if question_type not in matrix:
            raise errors.UnknownQuestionTypeError()
        return matrix.get(question_type)


class DefaultEditorQuestion(_EditorQuestion):
    kind = 'default_editor'

    def __init__(self, name, default_filename=None, **kwargs):
        super(DefaultEditorQuestion, self).__init__(name, **kwargs)
        self.default_filename = default_filename    # added by us


class DefaultEditor(_EditorRender):
    def __init__(self, *args, **kwargs):
        super(DefaultEditor, self).__init__(*args, **kwargs)
        self.default_filename = self.question.default_filename

    def process_input(self, pressed):
        if pressed == key.CTRL_C:
            raise KeyboardInterrupt()
        if pressed in (key.CR, key.LF, key.ENTER):
            data = editor.edit(
                filename=self.default_filename,     # added by us
                contents=self.question.default or ''
            )
            raise errors.EndOfInput(data.decode('utf-8'))

        raise errors.ValidationError(
            'You have pressed unknown key! Press <enter> to open '
            'editor or CTRL+C to exit.'
        )


class DefaultTheme(_DefaultTheme):
    def __init__(self):
        super(DefaultTheme, self).__init__()
        self.DefaultEditor = namedtuple('default_editor', 'opening_prompt')
        self.DefaultEditor.opening_prompt_color = _term.bright_black
