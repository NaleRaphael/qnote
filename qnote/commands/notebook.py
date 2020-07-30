from argparse import ArgumentParser
from .base_command import Command
from qnote.cli.parser import CustomArgumentParser


__all__ = ['NotebookCommand']


class NotebookCommand(Command):
    """Manage notebooks."""

    _usage = """
    <prog> create <name>
    <prog> delete <name> [-f | --force]
    <prog> list
    <prog> rename <old-name> <new-name>
    <prog> search <pattern>
    <prog> status
    """

    def __init__(self, *args, **kwargs):
        super(NotebookCommand, self).__init__(*args, **kwargs)

    def run(self, defined_args, config):
        raise NotImplementedError

    def prepare_parser(self):
        parser = ArgumentParser(prog=self.name, usage=self.usage)
        subparsers = parser.add_subparsers(dest='cmd', required=True)

        parser_create = subparsers.add_parser('create', prog='create')
        parser_create.add_argument(
            'name', metavar='<name>', help='Name of notebook.'
        )

        parser_delete = subparsers.add_parser('delete', prog='delete')
        parser_delete.add_argument(
            'name', metavar='<name>', help='Name of notebook.'
        )
        parser_delete.add_argument(
            '-f', '--force',
            help='Forcibly delete specified notebook.'
        )

        parser_list = subparsers.add_parser('list', prog='list')

        parser_rename = subparsers.add_parser('rename', prog='rename')
        parser_rename.add_argument(
            'old_name', metavar='<old-name>',
            help='Old name of target notebook to be renamed.'
        )
        parser_rename.add_argument(
            'new_name', metavar='<new-name>',
            help='New name of the target notebook to be renamed.'
        )

        parser_search = subparsers.add_parser('search', prog='search')
        parser_search.add_argument(
            'pattern', metavar='<pattern>',
            help='Pattern for searching notebooks.'
        )

        parser_status = subparsers.add_parser('status', prog='status')
        return parser
