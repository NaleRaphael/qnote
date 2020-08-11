from qnote.cli.parser import CustomArgumentParser, ARG_SUPPRESS
from qnote.internal.exceptions import SafeExitException
from qnote.manager import NotebookManager

from .base_command import Command

__all__ = ['SelectCommand']


class SelectCommand(Command):
    """Select a note. If no argument is given, interactive mode will start
    with an opened notebook."""

    _usage = """
    <prog> [--multiple] [--date] [--uuid]
    <prog> clear"""

    def __init__(self, *args, **kwargs):
        super(SelectCommand, self).__init__(*args, **kwargs)

    def run(self, parsed_args, config):
        kwargs, _ = parsed_args
        cmd = kwargs.pop('cmd')
        cmd = 'select' if cmd is None else cmd
        runner = getattr(self, '_run_%s' % cmd, None)
        if runner is None:
            raise RuntimeError('Invalid command: %s' % cmd)

        try:
            runner(kwargs, config)
        except SafeExitException as ex:
            print(ex)

    def prepare_parser(self):
        parser = CustomArgumentParser(
            prog=self.name, usage=self.usage, add_help=False,
            description=self.__doc__,
        )
        parser.add_argument(
            '--multiple', action='store_true',
            help=(
                'If this flag is set, user can select multiple notebooks in '
                'the interactive mode.'
            )
        )
        parser.add_argument(
            '--date', action='store_true',
            help='Show create_time and update_time of notes.'
        )
        parser.add_argument(
            '--uuid', action='store_true',
            help='Show uuid of notes.'
        )
        parser.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )

        subparsers = parser.add_subparsers(dest='cmd')
        parser_clear = subparsers.add_parser(
            'clear', prog='clear', add_help=False,
            description='Clear selected notes from cache.'
        )
        parser_clear.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )
        return parser

    def _run_select(self, parsed_kwargs, config):
        select_multiple = parsed_kwargs['multiple']
        show_date = parsed_kwargs['date']
        show_uuid = parsed_kwargs['uuid']

        NotebookManager(config).select_notes(
            multiple=select_multiple,
            show_date=show_date,
            show_uuid=show_uuid,
        )

    def _run_clear(self, parsed_kwargs, config):
        NotebookManager(config).clear_selected_notes()
