from datetime import datetime as dt
import textwrap as tw


__all__ = ['NoteFormatter']


class NoteFormatter(object):
    def __init__(self, app_config, tw_config=None, show_date=False, show_uuid=False):
        self.app_config = app_config
        self._prepare_textwrapper(**tw_config)
        self._prepare_subformatter(show_date=show_date, show_uuid=show_uuid)

    def _prepare_textwrapper(self, **kwargs):
        self.tw_config = {
            'width': kwargs.get('width', 70),
            'tabsize': kwargs.get('tabsize', 4),
            'replace_whitespace': kwargs.get('replace_whitespace', False),
            'drop_whitespace': kwargs.get('drop_whitespace', True),
            'max_lines': kwargs.get('max_lines', 3),
            'placeholder': kwargs.get('placeholder', '...'),
            'initial_indent': kwargs.get('initial_indent', '    '),
            'subsequent_indent': kwargs.get('subsequent_indent', '    '),
        }
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
