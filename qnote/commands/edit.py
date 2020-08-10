from argparse import SUPPRESS as ARG_SUPPRESS

from qnote.cli.parser import CustomArgumentParser, PassableHelpAction
from qnote.internal.exceptions import SafeExitException
from qnote.manager import NoteManager

from .base_command import Command

__all__ = ['EditCommand']


class EditCommand(Command):
    """Open a note for viewing only."""

    _usage = """
    <prog> [--uuid <note_uuid>] [--editor <editor_name>]
    <prog> selected [--editor <editor_name>]"""

    def __init__(self, *args, **kwargs):
        super(EditCommand, self).__init__(*args, **kwargs)

    def run(self, parsed_args, config):
        kwargs, _ = parsed_args
        cmd = kwargs.pop('cmd')
        cmd = 'edit' if cmd is None else cmd
        runner = getattr(self, '_run_%s' % cmd, None)

        try:
            # TODO: if we are going to find a note by uuid, we should
            # make it able to search by a part of uuid
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
                'UUID of the note to open. If this argument is not given, '
                'interactive mode will start and user can select a note from '
                'notebook.'
            )
        )
        parser.add_argument(
            '--editor_name', dest='editor_name', metavar='<editor_name>',
            help='Open and edit a note with specified editor.'
        )
        parser.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )

        parser_selected = subparsers.add_parser(
            'selected', prog='selected', aliases=['sel'], add_help=False,
            description='Open note from selected list (gerenated by `qnote select`).'
        )
        parser_selected.add_argument(
            '--editor_name', dest='editor_name', metavar='<editor_name>',
            help='Open and edit a note with specified editor.'
        )
        parser_selected.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )

        return parser

    def _run_edit(self, parsed_kwargs, config):
        uuid = parsed_kwargs['uuid']
        editor_name = parsed_kwargs['editor_name']
        NoteManager(config).edit_note(uuid, editor_name=editor_name)

    def _run_selected(self, parsed_kwargs, config):
        editor_name = parsed_kwargs['editor_name']
        NoteManager(config).edit_note_from_selected(editor_name=editor_name)

    # alias
    _run_sel = _run_selected
