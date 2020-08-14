from qnote.cli.parser import CustomArgumentParser, ARG_SUPPRESS
from qnote.internal.exceptions import SafeExitException
from qnote.manager import NoteManager

from .base_command import Command

__all__ = ['SearchCommand']


class SearchCommand(Command):
    """Search note by given pattern of UUID, title, content, tag."""

    _usage = """
    <prog> uuid <pattern_of_uuid>
    <prog> title <pattern_of_title>
    <prog> content <pattern_of_content>
    <prog> tags <tags>"""

    def __init__(self, *args, **kwargs):
        super(SearchCommand, self).__init__(*args, **kwargs)

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
        parser.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )

        subparsers = parser.add_subparsers(dest='cmd', required=True)
        parser_uuid = subparsers.add_parser(
            'uuid', prog='uuid', add_help=False,
            description=(
                'Search note by pattern of UUID. Note that hyphen "-" in UUID '
                'can be ignored, e.g. for a UUID "...685-5878...", we can use '
                '"8558" as a query.'
            )
        )
        parser_uuid.add_argument(
            'uuid', metavar='<pattern_of_uuid>',
            help='Pattern of UUID to search.'
        )
        parser_uuid.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )

        parser_title = subparsers.add_parser(
            'title', prog='title', add_help=False,
            description='Search note by pattern of title.'
        )
        parser_title.add_argument(
            'title', metavar='<pattern_of_title>',
            help='Pattern of title to search.'
        )
        parser_title.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )

        parser_content = subparsers.add_parser(
            'content', prog='content', add_help=False,
            description='Search note by pattern of content.'
        )
        parser_content.add_argument(
            'content', metavar='<pattern_of_content>',
            help='Pattern of content to search.'
        )
        parser_content.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )

        parser_tag = subparsers.add_parser(
            'tags', prog='tags', add_help=False,
            description='Search note by tags.'
        )
        parser_tag.add_argument(
            'tags', metavar='<tags>',
            help=(
                'Tag to search. If multiple values are given, they should be '
                'separated by commas and enclosed by quotation marks. e.g. '
                '"#tag_name_1, #tag_name_2, ..."'
            )
        )
        parser_tag.add_argument(
            '-h', '--help', action='help',
            default=ARG_SUPPRESS,
            help='Show this help message and exit.'
        )
        return parser

    def _run_uuid(self, parsed_kwargs, config):
        uuid = parsed_kwargs['uuid']
        NoteManager(config).search_note_by_uuid(uuid)

    def _run_title(self, parsed_kwargs, config):
        title = parsed_kwargs['title']
        NoteManager(config).search_note_by_title(title)

    def _run_content(self, parsed_kwargs, config):
        content = parsed_kwargs['content']
        NoteManager(config).search_note_by_content(content)

    def _run_tags(self, parsed_kwargs, config):
        tags = parsed_kwargs['tags']
        NoteManager(config).search_note_by_tags(tags)
