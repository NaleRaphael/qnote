from __future__ import absolute_import
import re, sys
from argparse import SUPPRESS as ARG_SUPPRESS

from qnote.cli.parser import CustomArgumentParser, PassableHelpAction
from qnote.config import AppConfig
from qnote.internal.exceptions import StorageCheckException
from qnote.storage import get_storer
import qnote.commands as cmds


__all__ = ['Application']


subcommands = {
    'add': cmds.AddCommand('add'),
    'help': cmds.HelpCommand('help'),
    'list': cmds.ListCommand('list'),
    'notebook': cmds.NotebookCommand('notebook'),
    'status': cmds.StatusCommand('status'),
}


def _process_usage(usage, delimiter='\n', skip_row=1, left_padding=0):
    splitted = usage.split(delimiter)
    padding_spaces = ' '*left_padding if left_padding >= 0 else ''
    padded = ['%s%s' % (padding_spaces, v) for v in splitted[skip_row:]]
    return delimiter.join([*splitted[:skip_row], *padded])


def prepare_usage():
    msg = '\n'
    temp = []
    n_padding = len('qnote') - 4    # 4: size of tab
    sub_usages = [
        '<prog> %s' % (
            _process_usage(sc.usage.lstrip(), left_padding=n_padding)
        ) for sc in subcommands.values()
    ]
    msg_subs = '\n'.join(sub_usages)
    msg += msg_subs
    regex = re.compile('<prog>')
    msg = regex.sub('qnote', msg)
    return msg


class CommandEntry(cmds.Command):
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
        )
        parser.add_argument(
            'cmd', metavar='cmd', choices=list(subcommands.keys()),
            help='Subcommands'
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
        self.initialize_storage()

    def initialize(self):
        self.config = AppConfig.load()

    def initialize_storage(self):
        # default notebook: "[DEFAULT]" and "[TRASH]" should be initialized
        nb_names = [
            self.config.notebook.name_default,
            self.config.notebook.name_trash,
        ]
        storer = get_storer(self.config)

        for name in nb_names:
            if not storer.check_notebook_exist(name):
                msg = (
                    'Storage is not initialized properly, please report '
                    'this error to developers: DEFAULT_NOTEBOOK_CREATION_FAULURE'
                )
                raise StorageCheckException(msg)

    def run(self):
        entry = CommandEntry('qnote')
        entry.main(sys.argv[1:], self.config)
