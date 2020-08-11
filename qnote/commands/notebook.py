from qnote.cli.parser import CustomArgumentParser, ARG_SUPPRESS
from qnote.internal.exceptions import SafeExitException
from qnote.manager import NotebookManager

from .base_command import Command


__all__ = ['NotebookCommand']


class NotebookCommand(Command):
    """Manage notebooks."""

    _usage = """
    <prog> open <name>
    <prog> create <name>
    <prog> delete <name> [-f | --force]
    <prog> list [--date]
    <prog> rename <old-name> <new-name>
    <prog> search <pattern>"""

    def __init__(self, *args, **kwargs):
        super(NotebookCommand, self).__init__(*args, **kwargs)

    def run(self, defined_args, config):
        kwargs, reminder = defined_args
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
            prog=self.name, usage=self.usage,
            description=self.__doc__,
        )
        subparsers = parser.add_subparsers(dest='cmd', required=True)

        parser_open = subparsers.add_parser(
            'open', prog='open',
            description='Open a notebook.'
        )
        parser_open.add_argument(
            'name', metavar='<name>', help='Name of notebook.'
        )

        parser_create = subparsers.add_parser(
            'create', prog='create',
            description='Create a notebook.'
        )
        parser_create.add_argument(
            'name', metavar='<name>', help='Name of notebook.'
        )

        parser_delete = subparsers.add_parser(
            'delete', prog='delete',
            description=(
                'Delete a notebook. Existing notes will be deleted permanently. '
                'Please consider using `qnote remove` to remove those notes '
                'to trash can before deleting a notebook if you are not sure '
                'that you really don\'t want to keep those notes.'
            )
        )
        parser_delete.add_argument(
            'name', metavar='<name>', help='Name of notebook.'
        )
        parser_delete.add_argument(
            '-f', '--force', action='store_true',
            help='Forcibly delete specified notebook.'
        )
        parser_delete.add_argument(
            '-y', '--yes', action='store_true',
            help='Automatically answer YES to the prompt for confirmation.'
        )

        parser_list = subparsers.add_parser(
            'list', prog='list',
            description='List all notebooks.'
        )
        parser_list.add_argument(
            '--date', action='store_true',
            help='Show create_time and update_time of notebooks.'
        )
        parser_list.add_argument(
            '-a', '--all', action='store_true',
            help='Show all notebooks including those ones for special purpose.'
        )

        parser_rename = subparsers.add_parser(
            'rename', prog='rename',
            description='Rename of notebook.'
        )
        parser_rename.add_argument(
            'old_name', metavar='<old-name>',
            help='Old name of target notebook to be renamed.'
        )
        parser_rename.add_argument(
            'new_name', metavar='<new-name>',
            help='New name of the target notebook to be renamed.'
        )

        parser_search = subparsers.add_parser(
            'search', prog='search',
            description='Search a notebook (regular expression is supported).'
        )
        parser_search.add_argument(
            'pattern', metavar='<pattern>',
            help='Pattern for searching notebooks.'
        )
        return parser

    def _run_create(self, parsed_kwargs, config):
        name = parsed_kwargs['name']
        NotebookManager(config).create_notebook(name)

    def _run_open(self, parsed_kwargs, config):
        name = parsed_kwargs['name']
        NotebookManager(config).open_notebook(name)

    def _run_list(self, parsed_kwargs, config):
        show_date = parsed_kwargs['date']
        show_all = parsed_kwargs['all']
        NotebookManager(config).list_all_notebooks(
            show_date=show_date, show_all=show_all
        )

    def _run_search(self, parsed_kwargs, config):
        raise NotImplementedError

    def _run_rename(self, parsed_kwargs, config):
        old_name = parsed_kwargs['old_name']
        new_name = parsed_kwargs['new_name']
        NotebookManager(config).rename_notebook(old_name, new_name)

    def _run_delete(self, parsed_kwargs, config):
        name = parsed_kwargs['name']
        forcibly = parsed_kwargs['force']
        yes = parsed_kwargs['yes']
        NotebookManager(config).delete_notebook(
            name, forcibly=forcibly, skip_confirmation=yes
        )
