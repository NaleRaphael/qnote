from qnote.cli.parser import CustomArgumentParser, ARG_SUPPRESS
from qnote.internal.exceptions import SafeExitException
from qnote.manager import NotebookManager
from qnote.utils import query_yes_no

from .base_command import Command


__all__ = ['ClearCommand']


class ClearCommand(Command):
    """Clear trash can. (all notes in it will be deleted permanently)"""

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
        parser = CustomArgumentParser(
            prog=self.name, usage=self.usage, add_help=False,
            description=self.__doc__,
        )
        parser.add_argument(
            '-y', '--yes', action='store_true',
            help='Automatically answer YES to the prompt for confirmation.'
        )
        parser.add_argument(
            '-h', '--help', action='help', default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )
        return parser
