from qnote.cli.parser import CustomArgumentParser, ARG_SUPPRESS
from qnote.internal.exceptions import SafeExitException
from qnote.manager import TagManager

from .base_command import Command

__all__ = ['TagCommand']


class TagCommand(Command):
    """Manage tags."""

    _usage = """
    <prog> list
    <prog> clear_empty"""

    def __init__(self, *args, **kwargs):
        super(TagCommand, self).__init__(*args, **kwargs)
        self.no_more_subcommands = True

    def run(self, parsed_args, config):
        kwargs, _ = parsed_args
        cmd = kwargs.pop('cmd')
        runner = getattr(self, '_run_%s' % cmd, None)
        if runner is None:
            raise RuntimeError('Invalid command: %s' % cmd)

        try:
            runner(kwargs, config)
        except SafeExitException as ex:
            print(ex)

    def prepare_parser(self):
        parser = CustomArgumentParser(
            prog=self.name, usage=self.usage, add_help=False,
            description=self.__doc__,
        )
        subparsers = parser.add_subparsers(dest='cmd', required=True)
        parser.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )

        parser_list = subparsers.add_parser(
            'list', prog='list', aliases=['ls'], add_help=False,
            description='List all tags with counts.'
        )
        parser_list.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )

        parser_clear_empty = subparsers.add_parser(
            'clear_empty', prog='clear_empty', aliases=['cle'], add_help=False,
            description='Clear those tags which no notes are tagged by.'
        )
        parser_clear_empty.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )
        return parser

    def _run_list(self, parsed_kwargs, config):
        TagManager(config).list_tags()

    _run_ls = _run_list

    def _run_clear_empty(self, parsed_kwargs, config):
        TagManager(config).clear_empty_tags()

    _run_cle = _run_clear_empty
