from qnote.cli.parser import CustomArgumentParser, ARG_SUPPRESS
from qnote.internal.exceptions import (
    SafeExitException,
    StorageCheckException,
)
from qnote.manager import NoteManager

from .base_command import Command

__all__ = ['MoveCommand']


class MoveCommand(Command):
    """Move specific notes to another notebook."""

    _usage = """
    <prog> [--uuid <note_uuid>] [--notebook <notebook_name>]
    <prog> selected [--notebook <notebook_name>]"""

    def __init__(self, *args, **kwargs):
        super(MoveCommand, self).__init__(*args, **kwargs)

    def run(self, parsed_args, config):
        kwargs, _ = parsed_args
        cmd = kwargs.pop('cmd')
        cmd = 'move' if cmd is None else cmd
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
                'UUID of the notes to move. If this argument is not given, '
                'interactive mode will start and user can select notes from '
                'notebook.'
            )
        )
        parser.add_argument(
            '--notebook', dest='notebook', metavar='<notebook_name>', required=True,
            help='Destination of the notes to moved into.'
        )
        parser.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )

        parser_selected = subparsers.add_parser(
            'selected', prog='selected', aliases=['sel'], add_help=False,
            description='Remove notes from selected list (gerenated by `qnote select`).'
        )
        parser_selected.add_argument(
            '--notebook', dest='notebook', metavar='<notebook_name>', required=True,
            help='Destination of the notes to moved into.'
        )
        parser_selected.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )

        return parser

    def _run_move(self, parsed_kwargs, config):
        uuid = parsed_kwargs['uuid']
        nb_name = parsed_kwargs['notebook']
        try:
            NoteManager(config).move_note(uuid, nb_name)
        except StorageCheckException as ex:
            raise SafeExitException(str(ex))

    def _run_selected(self, parsed_kwargs, config):
        nb_name = parsed_kwargs['notebook']
        try:
            NoteManager(config).move_note_from_selected(nb_name)
        except StorageCheckException as ex:
            raise SafeExitException(str(ex))

    # alias
    _run_sel = _run_selected
