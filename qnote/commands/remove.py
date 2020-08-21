from qnote.cli.parser import CustomArgumentParser, ARG_SUPPRESS
from qnote.internal.exceptions import SafeExitException
from qnote.manager import NoteManager

from .base_command import Command

__all__ = ['RemoveCommand']


class RemoveCommand(Command):
    """Remove specific notes to trash can."""

    _usage = """
    <prog> [--uuid <note_uuid>]
    <prog> selected"""

    def __init__(self, *args, **kwargs):
        super(RemoveCommand, self).__init__(*args, **kwargs)

    def run(self, parsed_args, config):
        kwargs, _ = parsed_args
        cmd = kwargs.pop('cmd')
        cmd = 'remove' if cmd is None else cmd
        runner = getattr(self, '_run_%s' % cmd, None)

        try:
            runner(kwargs, config)
        except SafeExitException as ex:
            print(ex)

    def prepare_parser(self):
        parser = CustomArgumentParser(
            prog=self.name, usage=self.usage, add_help=False,
            description=self.__doc__,
        )
        subparsers = parser.add_subparsers(dest='cmd')

        parser.add_argument(
            '--uuid', dest='uuid', metavar='<note_uuid>', default=None,
            help=(
                'UUID of the note to remove. If this argument is not given, '
                'interactive mode will start and user can select a note from '
                'notebook.'
            )
        )
        parser.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )

        parser_selected = subparsers.add_parser(
            'selected', prog='selected', aliases=['sel'], add_help=False,
            description='Remove note from selected list (gerenated by `qnote select`).'
        )
        parser_selected.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )

        return parser

    def _run_remove(self, parsed_kwargs, config):
        uuid = parsed_kwargs['uuid']
        # If no uuid is given, enter interactive to select note from current notebook
        NoteManager(config).remove_note(uuid)

    def _run_selected(self, parsed_kwargs, config):
        NoteManager(config).remove_note_from_selected()

    # alias
    _run_sel = _run_selected
