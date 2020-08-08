from argparse import SUPPRESS as ARG_SUPPRESS

from qnote.cli.parser import CustomArgumentParser
from qnote.internal.exceptions import SafeExitException
from qnote.manager import NotebookManager

from .base_command import Command

__all__ = ['SelectCommand']


class SelectCommand(Command):
    """Select a note. If no argument is given, interactive mode will start
    with opened notebook."""

    _usage = """
    <prog>"""

    def __init__(self, *args, **kwargs):
        super(SelectCommand, self).__init__(*args, **kwargs)
        self.no_more_subcommands = True

    def run(self, parsed_args, config):
        kwargs, _ = parsed_args
        select_multiple = kwargs['multiple']
        show_date = kwargs['date']
        show_uuid = kwargs['uuid']

        try:
            NotebookManager(config).select_notes(
                multiple=select_multiple,
                show_date=show_date,
                show_uuid=show_uuid,
            )
        except SafeExitException as ex:
            print(ex)

    def prepare_parser(self):
        parser = CustomArgumentParser(
            prog=self.name, usage=self.usage, add_help=False,
        )
        parser.add_argument(
            '--multiple', action='store_true',
            help=(
                'If this flag is set, user can select multiple notebook in '
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
        return parser
