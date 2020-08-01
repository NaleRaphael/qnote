from argparse import ArgumentParser
from contextlib import contextmanager
import re

from qnote.cli.parser import CustomArgumentParser


__all__ = ['Command']


class Command(object):
    """Basic command class."""

    _usage = None

    def __init__(self, name):
        """
        Parameters
        ----------
        name : str
            Name of this command.
        """
        super(Command, self).__init__()
        self.name = name
        self.description = self.__doc__
        self.no_more_subcommands = False
        self._parent = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        if not isinstance(value, Command):
            raise TypeError('`value` should be an instance of %s' % Command)
        self._parent = value

    @property
    def usage(self):
        parent_name = '' if self.parent is None else self.parent.name
        prog_name = '%s %s' % (parent_name, self.name)
        return re.compile('<prog>').sub(prog_name, self._usage)

    def run(self, parsed_args, config):
        """Run command.

        Parameters
        ----------
        parsed_args : tuple, (known_args, unknown_args)
        config : qnote.config.AppConfig
        """
        raise NotImplementedError

    def prepare_parser(self):
        raise NotImplementedError

    def main(self, argv, config):
        self.run(self.parse_args(argv), config)

    def parse_args(self, args):
        """Parse defined arguments for command according to the parser returned
        from `self.prepare_parser()`.

        Note that if `self.no_more_subcommands` is True, `parse_args()` will be
        used instead. It means "error: unrecognized arguments" will be raised if
        there is any undefined arguments remaining.

        Parameters
        ----------
        args : list
            List of arguments.

        Returns
        -------
        known_args : dict
            List of arguments which were stated in parser.
        unkown_args : list
            List of arguments which were not stated in parser.
        """
        parser = self.prepare_parser()
        assert isinstance(parser, (ArgumentParser, CustomArgumentParser))

        if self.no_more_subcommands:
            return vars(parser.parse_args(args)), []
        else:
            known_args, unknown_args = parser.parse_known_args(args)
            return vars(known_args), unknown_args
