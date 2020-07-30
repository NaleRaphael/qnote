from .base_command import Command


__all__ = ['HelpCommand']


class HelpCommand(Command):
    """Show help for commands."""

    _usage = """
    <prog> <command>"""

    def __init__(self, *args, **kwargs):
        super(HelpCommand, self).__init__(*args, **kwargs)

    def run(self, parsed_args, config):
        raise NotImplementedError

    def prepare_parser(self):
        raise NotImplementedError
