from collections import namedtuple
from readchar import key
import sys

import editor   # python-editor, a dependency of python-inquirer
from inquirer import errors
from inquirer.render.console import ConsoleRender as _ConsoleRender
from inquirer.render.console import (
    Text, Editor, Password, Confirm, List, Checkbox, Path
)
from inquirer.themes import Default as _DefaultTheme
from inquirer.themes import term as _term
from inquirer.questions import (
    Question,
    List as ListQuestion,
)


__all__ = [
    'ConsoleRender', 'DefaultTheme',
    'DefaultEditor', 'DefaultEditorQuestion',
    'ListBox', 'ListBoxQuestion', 'ListBoxRender',
]


MAX_OPTIONS_IN_DISPLAY = 5
half_options = int((MAX_OPTIONS_IN_DISPLAY - 1) / 2)


class ConsoleRender(_ConsoleRender):
    def __init__(self, event_generator=None, theme=None, *args, **kwargs):
        super(ConsoleRender, self).__init__(*args, **kwargs)

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


class ListBoxRender(_ConsoleRender):
    def __init__(self, event_generator=None, theme=None, *args, **kwargs):
        self.render_config = kwargs.pop('render_config', {})
        self._printed_lines = 0
        super(ListBoxRender, self).__init__(*args, **kwargs)

    def render(self, question, answers=None):
        question.answers = answers or {}

        if question.ignore:
            return question.default

        clazz = self.render_factory(question.kind)
        render = clazz(
            question,
            terminal=self.terminal,
            theme=self._theme,
            show_default=question.show_default,
            render_config=self.render_config,
        )

        self.clear_eos()

        try:
            return self._event_loop(render)
        finally:
            print('')

    def render_factory(self, question_type):
        matrix = {
            'text': Text,
            'editor': Editor,
            'password': Password,
            'confirm': Confirm,
            'list': List,
            'listbox': ListBox,     # added for custom `ListBox` question
            'checkbox': Checkbox,
            'path': Path,
        }

        if question_type not in matrix:
            raise errors.UnknownQuestionTypeError()
        return matrix.get(question_type)

    def _count_lines(self, msg):
        self._printed_lines += msg.count('\n') + 1

    def _reset_counter(self):
        self._printed_lines = 0

    def _print_options(self, render):
        for message, symbol, color in render.get_options():
            if hasattr(message, 'decode'):  # python 2
                message = message.decode('utf-8')
            self._count_lines(message)      # count lines to be erased
            self.print_line(' {color}{s} {m}{t.normal}',
                            m=message, color=color, s=symbol)

    def _print_header(self, render):
        base = render.get_header()

        header = (base[:self.width - 9] + '...'
                  if len(base) > self.width - 6
                  else base)
        default_value = ' ({color}{default}{normal})'.format(
            default=render.question.default,
            color=self._theme.Question.default_color,
            normal=self.terminal.normal
        )
        show_default = render.question.default and render.show_default
        header += default_value if show_default else ''
        msg_template = "{t.move_up}{t.clear_eol}{tq.brackets_color}["\
                       "{tq.mark_color}?{tq.brackets_color}]{t.normal} {msg}"

        self._count_lines(header)       # count lines to be erased
        self.print_str(
            '\n%s:' % (msg_template),
            msg=header,
            lf=not render.title_inline,
            tq=self._theme.Question)

    def _relocate(self):
        move_up, clear_eol = self.terminal.move_up(), self.terminal.clear_eol()
        clear_lines = lambda n: (move_up + clear_eol) * n

        if self._printed_lines > 0:
            term_refresh_code = clear_lines(self._printed_lines)
            print(term_refresh_code, end='', flush=True)
            self._reset_counter()

        self._force_initial_column()
        self._position = 0


class DefaultEditorQuestion(Question):
    kind = 'default_editor'

    def __init__(self, name, default_filename=None, **kwargs):
        super(DefaultEditorQuestion, self).__init__(name, **kwargs)
        self.default_filename = default_filename    # added by us


class DefaultEditor(Editor):
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


class ListBoxQuestion(ListQuestion):
    kind = 'listbox'

    def __init__(self, name, **kwargs):
        super(ListBoxQuestion, self).__init__(name, **kwargs)


class ListBox(List):
    def __init__(self, *args, **kwargs):
        render_config = kwargs.pop('render_config', {})
        self.max_options_in_display = render_config.get(
            'n_max_options', MAX_OPTIONS_IN_DISPLAY
        )
        self.half_options = int((self.max_options_in_display - 1) / 2)
        super(ListBox, self).__init__(*args, **kwargs)

    @property
    def is_long(self):
        choices = self.question.choices or []
        return len(choices) >= self.max_options_in_display

    def get_options(self):
        choices = self.question.choices or []
        if self.is_long:
            cmin = 0
            cmax = self.max_options_in_display

            if self.half_options < self.current < len(choices) - self.half_options:
                cmin += self.current - self.half_options
                cmax += self.current - self.half_options
            elif self.current >= len(choices) - self.half_options:
                cmin += len(choices) - self.max_options_in_display
                cmax += len(choices)

            cchoices = choices[cmin:cmax]
        else:
            cchoices = choices

        ending_milestone = max(len(choices) - self.half_options, self.half_options + 1)
        is_in_beginning = self.current <= self.half_options
        is_in_middle = self.half_options < self.current < ending_milestone
        is_in_end = self.current >= ending_milestone

        for index, choice in enumerate(cchoices):
            end_index = ending_milestone + index - self.half_options - 1
            if (is_in_middle and index == self.half_options) \
                    or (is_in_beginning and index == self.current) \
                    or (is_in_end and end_index == self.current):

                color = self.theme.List.selection_color
                symbol = self.theme.List.selection_cursor
            else:
                color = self.theme.List.unselected_color
                symbol = ' '
            yield choice, symbol, color


class DefaultTheme(_DefaultTheme):
    def __init__(self):
        super(DefaultTheme, self).__init__()
        self.DefaultEditor = namedtuple('default_editor', 'opening_prompt')
        self.DefaultEditor.opening_prompt_color = _term.bright_black
