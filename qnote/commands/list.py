from .base_command import Command


__all__ = ['ListCommand']


class ListCommand(Command):
    """List all notes in a notebook."""

    _usage = """
    <prog>"""

    def __init__(self, *args, **kwargs):
        super(ListCommand, self).__init__(*args, **kwargs)

    def run(self, parsed_args, config):
        raise NotImplementedError

    def prepare_parser(self):
        raise NotImplementedError

