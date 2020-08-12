from __future__ import absolute_import
import re, sys

from qnote.cli.parser import CustomArgumentParser, PassableHelpAction, ARG_SUPPRESS
from qnote.config import AppConfig
from qnote.internal.exceptions import StorageCheckException
from qnote.storage import get_storer
import qnote.commands as cmds


__all__ = ['Application']


subcommands = {
    'add': cmds.AddCommand('add'),
    'clear': cmds.ClearCommand('clear'),
    'edit': cmds.EditCommand('edit'),
    'list': cmds.ListCommand('list'),
    'notebook': cmds.NotebookCommand('notebook'),
    'open': cmds.OpenCommand('open'),
    'remove': cmds.RemoveCommand('remove'),
    'status': cmds.StatusCommand('status'),
    'select': cmds.SelectCommand('select'),
}


def _process_usage(usage, delimiter='\n', skip_row=1, left_padding=0):
    splitted = usage.split(delimiter)
    padding_spaces = ' '*left_padding if left_padding >= 0 else ''
    padded = ['%s%s' % (padding_spaces, v) for v in splitted[skip_row:]]
    return delimiter.join([*splitted[:skip_row], *padded])


def prepare_usage():
    msg = '\n'
    temp = []
    n_padding = len('qnote')
    sub_usages = [
        '<prog> %s' % (
            _process_usage(sc.usage.lstrip(), left_padding=n_padding)
        ) for sc in subcommands.values()
    ]
    msg_subs = '\n'.join(sub_usages)
    msg += msg_subs
    regex = re.compile('<prog>')
    msg = regex.sub('    qnote', msg)
    return msg


class CommandEntry(cmds.Command):
    """qnote - Take notes quickly

    A command line note-taking tool.
    """

    def __init__(self, *args, **kwargs):
        super(CommandEntry, self).__init__(*args, **kwargs)

    def run(self, parsed_args, config):
        known_args, unknown_args = parsed_args
        runner = subcommands[known_args.pop('cmd')]
        runner.parent = self
        runner.main(unknown_args, config)

    def prepare_parser(self):
        parser = CustomArgumentParser(
            prog='qnote', usage=prepare_usage(), add_help=False,
            description=self.__doc__,
        )
        parser.add_argument(
            'cmd', metavar='cmd', choices=list(subcommands.keys()),
            help='One of {%s}' % ', '.join(subcommands.keys()),
        )
        parser.add_argument(
            '-h', '--help', action=PassableHelpAction,
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )
        return parser


class Application(object):
    def __init__(self):
        self.initialize()

    def initialize(self):
        self.config = AppConfig.load()

    def run(self):
        entry = CommandEntry('qnote')
        entry.main(sys.argv[1:], self.config)
