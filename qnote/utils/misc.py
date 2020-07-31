import sys


__all__ = ['query_yes_no']


def query_yes_no(question, default='yes', back_n_lines=0):
    # Modified solution from: https://stackoverflow.com/a/3041990
    valid = {'yes': True, 'y': True, 'ye': True, 'no': False, 'n': False}
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError('invalid default answer: \'%s\'' % default)

    # ANSI control code
    code_back = '' if back_n_lines == 0 else '\x1b[%sA' % back_n_lines

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write(
                '%sPlease respond with \'yes\' or \'no\' '
                '(or \'y\' or \'n\').\n' % code_back
            )
