from datetime import datetime as dt
import textwrap as tw


__all__ = ['NoteFormatter', 'show_notes']


class NoteFormatter(object):
    def __init__(self, app_config, tw_config=None, show_date=False, show_uuid=False):
        self.app_config = app_config
        self._prepare_textwrapper(**tw_config)
        self._prepare_subformatter(show_date=show_date, show_uuid=show_uuid)

    def _prepare_textwrapper(self, **kwargs):
        cfg = self.app_config.display
        keys = [
            'width', 'tabsize', 'replace_whitespace', 'drop_whitespace',
            'max_lines', 'placeholder', 'initial_indent', 'subsequent_indent',
        ]
        self.tw_config = {k: getattr(cfg, k) for k in keys}
        self.text_wrapper = tw.TextWrapper(**self.tw_config)

    def _prepare_subformatter(self, show_date=False, show_uuid=False):
        fmt_time = '%Y-%m-%d %H:%M:%S'

        text_shortener = lambda text: tw.shorten(
            text, width=self.tw_config['width'], placeholder='...'
        )
        text_indenter = lambda text: '\n'.join(self.text_wrapper.wrap(text))
        fmt_uuid = lambda x: 'UUID: %s' % x.uuid
        fmt_title = lambda x: 'Title: %s' % text_shortener(x.title)
        fmt_tags = lambda x: 'Tags: %s' % text_shortener(str(x.tags))
        fmt_content = lambda x: 'Content:\n%s' % text_indenter(x.content.to_format(str))
        fmt_cuime = lambda x: 'Created: %s, Updated: %s' % (
            dt.fromtimestamp(x.create_time).strftime(fmt_time),
            dt.fromtimestamp(x.update_time).strftime(fmt_time)
        )

        formatters = [fmt_title, fmt_tags]
        if show_date:
            formatters.append(fmt_cuime)
        if show_uuid:
            formatters = [fmt_uuid, *formatters]
        formatters.append(fmt_content)
        self.formatter = formatters

    def __call__(self, note):
        return '\n'.join([fmt(note) for fmt in self.formatter])


class Pager(object):
    def __init__(self, app_config):
        self.app_config = app_config

    def __call__(self, content):
        raise NotImplementedError


class LessPager(Pager):
    # Reference of redirecting content to `less` (without creating a tempfile)
    # https://chase-seibert.github.io/blog/2012/10/31/python-fork-exec-vim-raw-input.html

    def __call__(self, content):
        from subprocess import Popen, PIPE
        from sys import stdout

        if not isinstance(content, (str, bytes)):
            raise TypeError('Unknown input type for paging.')

        try:
            cmd = ['less', '-F', '-R', '-S', '-X', '-K']
            proc = Popen(cmd, stdin=PIPE, stdout=stdout)

            if isinstance(content, str):
                proc._stdin_write(content.encode())
            else:
                proc._stdin_write(content)

            proc.stdin.close()
            proc.wait()
        except KeyboardInterrupt:
            pass


class PydocPager(Pager):
    def __call__(self, content):
        import pydoc

        pydoc.pager(content)


available_pagers = {
    'less': LessPager,
    'pydoc': PydocPager,
}

def prepare_pager(app_config):
    pager_name = app_config.display.pager
    cls_pager = available_pagers.get(pager_name, PydocPager)
    return cls_pager(app_config)


def show_notes(notes, app_config, tw_config, show_date=True, show_uuid=True):
    pager = prepare_pager(app_config)

    # Setup formatter
    formatter = NoteFormatter(
        app_config,
        tw_config=tw_config,
        show_date=show_date,
        show_uuid=show_uuid
    )

    # Print notes
    output = ''
    for note in notes:
        output += '\n%s\n' % formatter(note)
    pager(output)
