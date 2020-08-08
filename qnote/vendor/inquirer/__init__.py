# Prevent the warning message "Could not find terminal cygwin"
# showing up for cygwin after importing python-inquirer.
# import warnings
# with warnings.catch_warnings():
#     warnings.simplefilter('ignore', category=UserWarning)
#     import inquirer
# del warnings

# - Second approach:
#   Note that forcibly set environment variable `TERM` to "xterm" might
#   result in display issue on the terminal.

import os
term = os.getenv('TERM', None)
if term == 'cygwin':
    os.environ['TERM'] = 'xterm'

import inquirer
from inquirer import *
from .customization import *


__all__ = []
__all__.extend(inquirer.__all__)
__all__.extend(customization.__all__)

del inquirer
