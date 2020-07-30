from .base_command import Command
from qnote.cli.parser import CustomArgumentParser


__all__ = ['AddCommand']


class AddCommand(Command):
    """Add a new note."""

    _usage = """
    <prog> [-c | --content] [-t | --tags <tag1>, <tag2>]"""

    def __init__(self, *args, **kwargs):
        super(AddCommand, self).__init__(*args, **kwargs)
        self.no_more_subcommands = True

    def run(self, parsed_args, config):
        raise NotImplementedError

    def prepare_parser(self):
        parser = CustomArgumentParser(prog=self.name, usage=self.usage)
        parser.add_argument(
            '-c', '--content', dest='content',
            help='Content of note.'
        )
        parser.add_argument(
            '-t', '--tags', dest='tags',
            help=('Tags of note, should be separated by commas if multiple'
            'tags is given.')
        )
        return parser
