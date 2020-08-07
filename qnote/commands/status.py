from argparse import SUPPRESS as ARG_SUPPRESS

from qnote.cli.parser import CustomArgumentParser
from qnote.internal.exceptions import SafeExitException
from qnote.manager import NotebookManager

from .base_command import Command


__all__ = ['StatusCommand']


class StatusCommand(Command):
    """Show status of an notebook. If no notebook is specified, status of
    current notebook (which is pointed by `HEAD`) will be shown."""

    _usage = """
    <prog> [<notebook_name>]"""

    def __init__(self, *args, **kwargs):
        super(StatusCommand, self).__init__(*args, **kwargs)
        self.no_more_subcommands = True

    def run(self, parsed_args, config):
        kwargs, _ = parsed_args
        name = kwargs.get('name', None)

        try:
            NotebookManager(config).show_status(name)
        except SafeExitException as ex:
            print(ex)

    def prepare_parser(self):
        parser = CustomArgumentParser(
            prog=self.name, usage=self.usage, add_help=False,
        )
        parser.add_argument(
            'name', metavar='<notebook_name>', nargs='?', default=None,
            help='Name of notebook.'
        )
        parser.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )
        return parser
