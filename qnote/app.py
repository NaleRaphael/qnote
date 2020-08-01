from __future__ import absolute_import
import re, sys
from argparse import SUPPRESS as ARG_SUPPRESS

from qnote.cli.parser import CustomArgumentParser, PassableHelpAction
from qnote.config import AppConfig
import qnote.commands as cmds


__all__ = ['Application']


subcommands = {
    'add': cmds.AddCommand('add'),
    'help': cmds.HelpCommand('help'),
    'list': cmds.ListCommand('list'),
    'notebook': cmds.NotebookCommand('notebook'),
}

def prepare_usage():
    msg = '\n'
    msg_subs = '\n'.join([('  <prog> %s' % v.usage.lstrip())for k, v in subcommands.items()])
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

    def initialize(self):
        self.config = AppConfig.load()

    def run(self):
        entry = CommandEntry('qnote')
        entry.main(sys.argv[1:], self.config)
