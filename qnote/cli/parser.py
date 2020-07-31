from argparse import ArgumentParser
from gettext import gettext as _
import sys as _sys


__all__ = ['CustomArgumentParser']


class CustomArgumentParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(CustomArgumentParser, self).__init__(*args, **kwargs)

    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            msg = _('got unrecognized arguments: %s')
            self.error(msg % ' '.join(argv))
        return args

    def error(self, message):
        self.print_usage(_sys.stderr)
        args = {'prog': self.prog, 'message': message}
        self.exit(2, _('%(prog)s: error: %(message)s\n') % args)
