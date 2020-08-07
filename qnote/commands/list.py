from qnote.cli.parser import CustomArgumentParser
from qnote.internal.exceptions import SafeExitException
from qnote.manager import NotebookManager

from .base_command import Command


__all__ = ['ListCommand']


class ListCommand(Command):
    """List all notes in a notebook."""

    _usage = """
    <prog> [--date] [--uuid]"""

    def __init__(self, *args, **kwargs):
        super(ListCommand, self).__init__(*args, **kwargs)
        self.no_more_subcommands = True

    def run(self, parsed_args, config):
        kwargs, _ = parsed_args
        show_date = kwargs['date']
        show_uuid = kwargs['uuid']

        try:
            NotebookManager(config).show_all_notes(
                show_date=show_date,
                show_uuid=show_uuid,
            )
        except SafeExitException as ex:
            print(ex)

    def prepare_parser(self):
        parser = CustomArgumentParser(
            prog = self.name, usage=self.usage, add_help=False,
        )
        parser.add_argument(
            '--date', action='store_true',
            help='Show create_time and update_time of notes.'
        )
        parser.add_argument(
            '--uuid', action='store_true',
            help='Show uuid of notes.'
        )
        return parser
