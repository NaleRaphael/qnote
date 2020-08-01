from argparse import ArgumentParser, Action
from argparse import SUPPRESS as ARG_SUPPRESS
from gettext import gettext as _
import sys as _sys


__all__ = ['CustomArgumentParser', 'PassableHelpAction']


class CustomArgumentParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(CustomArgumentParser, self).__init__(*args, **kwargs)
        self._cached_args = None

    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            msg = _('got unrecognized arguments: %s')
            self.error(msg % ' '.join(argv))
        return args

    def parse_known_args(self, args=None, namespace=None):
        self._cached_args = _sys.argv[1:] if args is None else list(args)

        retval = super(CustomArgumentParser, self).parse_known_args(
            args=args, namespace=namespace
        )
        namespace, extras = retval

        # XXX: Extract 'help' from namespace
        optional_actions = self._get_optional_actions()
        for opt in optional_actions:
            if (isinstance(opt, PassableHelpAction) and
                hasattr(namespace, opt.dest)):
                extras.append('--help')
                delattr(namespace, opt.dest)
                break

        self._cached_args = None
        return namespace, extras

    def error(self, message):
        self.print_usage(_sys.stderr)
        args = {'prog': self.prog, 'message': message}
        self.exit(2, _('%(prog)s: error: %(message)s\n') % args)


class PassableHelpAction(Action):
    """A `HelpAction` that can be passed if there are existing
    positional arguments. (can be used to customize subparsers)"""
    def __init__(
        self, option_strings, dest=ARG_SUPPRESS, default=ARG_SUPPRESS,
        help=None
    ):
        super(PassableHelpAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(parser, CustomArgumentParser):
            assert parser._cached_args is not None, (
                'args was not cached properly, this might be an '
                'implementation error'
            )
            arg_strings = parser._cached_args
        else:
            # Might not work properly if not using `CustomArgumentParser`
            # since we can only access arguments from `sys.argv`. That is,
            # we cannot access the real arguments if those arguments are
            # passed by `parser.parse_args(args=REAL_ARGUMENTS)`.
            arg_strings = _sys.argv[1:] if len(_sys.argv) > 1 else []

        if (any([(v in arg_strings) for v in self.option_strings]) and
            len(arg_strings) <= 1):
            parser.print_help()
            parser.exit()
        else:
            setattr(namespace, self.dest, True)
