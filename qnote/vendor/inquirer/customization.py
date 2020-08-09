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
from inquirer import events


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
        self.message_handler = self.render_config.pop('message_handler', None)
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

    def _event_loop(self, render):
        need_to_rerender = True
        try:
            while True:
                if need_to_rerender:
                    self._relocate()
                    self._print_status_bar(render)

                    self._print_header(render)
                    self._print_options(render)

                    need_to_rerender = self._process_input(render)
                    self._force_initial_column()
                else:
                    need_to_rerender = self._process_input(render)
        except errors.EndOfInput as e:
            self._go_to_end(render)
            return e.selection

    def _count_lines(self, msg):
        self._printed_lines += msg.count('\n') + 1

    def _reset_counter(self):
        self._printed_lines = 0

    def _print_options(self, render):
        for message, symbol, color in render.get_options():
            if self.message_handler is not None:
                message = self.message_handler(message)

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

    def _process_input(self, render):
        try:
            ev = self._event_gen.next()
            if isinstance(ev, events.KeyPressed):
                # Return this to check whether it have to rerender
                return render.process_input(ev.value)
        except errors.ValidationError as e:
            self._previous_error = e.value
        except errors.EndOfInput as e:
            try:
                render.question.validate(e.selection)
                raise
            except errors.ValidationError as e:
                self._previous_error = render.handle_validation_error(e)
        return True


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
        self.choices_searcher = render_config.get(
            'choices_searcher', None
        )
        self.search_pattern = None
        self.n_current_choices = self.max_options_in_display
        self.half_options = int((self.max_options_in_display - 1) / 2)

        # NOTE: This should not be initialized to [], because we have to check
        # the selected choices is valid when `key.Enter` is pressed. See also
        # `process_input()` for further details.
        self.filtered_choices = None
        super(ListBox, self).__init__(*args, **kwargs)

    @property
    def is_long(self):
        choices = self.question.choices or []
        return len(choices) >= self.max_options_in_display

    def get_options(self):
        if self.filtered_choices is None:
            choices = self.question.choices or []
        else:
            choices = self.filtered_choices

        # Process with search mode
        if self.choices_searcher is not None and self.search_pattern is not None:
            if self.search_pattern == '/q':
                choices = self.question.choices or []
                self.filtered_choices = None    # reset
            else:
                choices = self.choices_searcher(choices, self.search_pattern)
                self.filtered_choices = choices
            self.search_pattern = None          # reset
            self.current = 0

        self.n_current_choices = len(choices)

        if self.is_long:
            # TODO: change the style of keeping chosen item in the middle.
            # Becasue it may lead to some problem while number of
            # `self.filtered_choices` is not odd.
            cmin = 0
            if self.filtered_choices is not None:
                cmax = len(self.filtered_choices)
            else:
                cmax = self.max_options_in_display
            half_options = int((cmax - 1) / 2)

            if half_options < self.current < len(choices) - half_options:
                cmin += self.current - half_options
                cmax += self.current - half_options
            elif self.current >= len(choices) - half_options:
                cmin += len(choices) - cmax
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

    def process_input(self, pressed):
        question = self.question
        if pressed == key.UP:
            if question.carousel and self.current == 0:
                self.current = len(question.choices) - 1
                return True
            else:
                # this should be determined before changing `self.current`
                need_to_rerender = self.current != 0
                self.current = max(0, self.current - 1)
                return need_to_rerender
        if pressed == key.DOWN:
            if question.carousel and self.current == len(question.choices) - 1:
                self.current = 0
                return True
            else:
                # this should be determined before changing `self.current`
                need_to_rerender = self.current != (self.n_current_choices - 1)
                self.current = min(
                    # len(self.question.choices) - 1,
                    self.n_current_choices - 1,
                    self.current + 1
                )
                return need_to_rerender
        if pressed == key.ENTER:
            if self.filtered_choices is not None:
                # We are under the search mode
                if len(self.filtered_choices) != 0:
                    value = self.filtered_choices[self.current]
                else:
                    raise errors.EndOfInput(None)
            else:
                value = self.question.choices[self.current]
            raise errors.EndOfInput(getattr(value, 'value', value))

        # Search mode related
        if pressed == '/':
            if self.choices_searcher is None:
                # Searcher is no available, so that search mode is disabled.
                return False
            pattern = input('Enter pattern to search (enter "/q" to quit): ')
            self.search_pattern = pattern
            clear_code = self.terminal.move_up() + self.terminal.clear_eol()
            print(clear_code*2)
            return True

        if pressed == key.CTRL_C:
            raise KeyboardInterrupt()


class DefaultTheme(_DefaultTheme):
    def __init__(self):
        super(DefaultTheme, self).__init__()
        self.DefaultEditor = namedtuple('default_editor', 'opening_prompt')
        self.DefaultEditor.opening_prompt_color = _term.bright_black
