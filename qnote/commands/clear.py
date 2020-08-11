from qnote.cli.parser import CustomArgumentParser
from qnote.internal.exceptions import SafeExitException
from qnote.manager import NotebookManager
from qnote.utils import query_yes_no

from .base_command import Command


__all__ = ['ClearCommand']


class ClearCommand(Command):
    """Clear trash can."""

    _usage = """
    <prog> [-y | --yes]"""

    def __init__(self, *args, **kwargs):
        super(ClearCommand, self).__init__(*args, **kwargs)

    def run(self, defined_args, config):
        kwargs, reminder = defined_args
        yes = kwargs.pop('yes')

        try:
            NotebookManager(config).clear_trash_can(skip_confirmation=yes)
        except SafeExitException as ex:
            print(ex)

    def prepare_parser(self):
        parser = CustomArgumentParser(prog=self.name, usage=self.usage)
        parser.add_argument(
            '-y', '--yes', action='store_true',
            help='Automatically answer YES to the prompt for confirmation.'
        )
        return parser
