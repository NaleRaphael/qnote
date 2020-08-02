from argparse import SUPPRESS as ARG_SUPPRESS

from qnote.cli.parser import CustomArgumentParser
from qnote.objects import Content, Note, Tags
from qnote.manager import NoteManager

from .base_command import Command

__all__ = ['AddCommand']


class AddCommand(Command):
    """Add a new note."""

    _usage = """
    <prog> [-c | --content <content>] [-t | --tags <tags>]"""

    def __init__(self, *args, **kwargs):
        super(AddCommand, self).__init__(*args, **kwargs)
        self.no_more_subcommands = True

    def run(self, parsed_args, config):
        kwargs, _ = parsed_args
        raw_content, raw_tags = kwargs['content'], kwargs['tags']
        NoteManager(config).create_note(raw_content, raw_tags)

    def prepare_parser(self):
        parser = CustomArgumentParser(
            prog=self.name, usage=self.usage, add_help=False,
        )
        parser.add_argument(
            '-c', '--content', dest='content', metavar='<content>',
            help='Content of note.'
        )
        parser.add_argument(
            '-t', '--tags', dest='tags', metavar='<tags>',
            help=(
                'Tags of note, should be separated by commas if multiple'
                'tags is given. '
                'e.g. --tags \"#tag1, #tag2, ...\"'
            )
        )
        parser.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )
        return parser
