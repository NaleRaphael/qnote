import os
import os.path as osp
import json


__all__ = ['AppConfig']


def check_all_keys_exist(template, target):
    if not isinstance(template, dict):
        raise TypeError('`template` should be a dict, got %s' % type(template))
    if not isinstance(target, dict):
        raise TypeError('`target` should be a dict, got %s' % type(target))

    for k, v in template.items():
        if k not in target:
            return False
        if isinstance(v, dict):
            if not check_all_keys_exist(v, target[k]):
                return False
    return True


class Defaults(object):
    pass


class ConfigBase(object):
    """
    name : str
        Name of config class.
    keys : list
        Keys to control customizable attributes. If an attribute name is
        not listed in this list, it would not be writen into the config
        file. So that user cannot modify it.
    """
    name = ''
    keys = []

    def __init__(self):
        pass

    def to_dict(self):
        return {k: getattr(self, k) for k in self.keys}

    def _check_remaining_kwargs(self, **kwargs):
        # Check whether there are remaining values for configuration
        if len(kwargs) != 0:
            import warnings
            msg = (
                f'{self.name}: There are unknown configuration values, '
                f'did you added them by accident? {kwargs}'
            )
            warnings.warn(msg, RuntimeWarning)


class AppDefaults(Defaults):
    dir_home = os.getenv('HOME', osp.expanduser('~'))
    dir_config = osp.join(dir_home, '.qnote')
    fn_config = osp.join(dir_config, 'config.json')
    fn_cached_note_uuid = osp.join(dir_config, 'CACHED_NOTE_UUID')


class AppConfig(ConfigBase):
    name = 'app'

    def __init__(self, **kwargs):
        super(AppConfig, self).__init__()
        if kwargs is None:
            kwargs = {}     # first initialization
        self.display = DisplayConfig(
            **kwargs.pop(DisplayConfig.name, {})
        )
        self.editor = EditorConfig(
            **kwargs.pop(EditorConfig.name, {})
        )
        self.storage = StorageConfig(
            **kwargs.pop(StorageConfig.name, {})
        )
        self.note = NoteConfig(
            **kwargs.pop(NoteConfig.name, {})
        )
        self.tag = TagConfig(
            **kwargs.pop(TagConfig.name, {})
        )
        self.notebook = NotebookConfig(
            **kwargs.pop(NotebookConfig.name, {})
        )
        self.fn_cached_note_uuid = AppDefaults.fn_cached_note_uuid
        self._check_remaining_kwargs(**kwargs)

    @classmethod
    def load(cls):
        if not osp.exists(AppDefaults.fn_config):
            # Config file does not exist, so we create it with default values
            config = cls()
            config.write()
            return config
        else:
            with open(AppDefaults.fn_config, 'r') as f:
                content = json.load(f)

            # Update config file if there are missing keys
            config = cls(**content)
            if not check_all_keys_exist(config.to_dict(), content):
                config.write()
            return config

    def write(self):
        os.makedirs(AppDefaults.dir_config, exist_ok=True)
        with open(AppDefaults.fn_config, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def to_dict(self):
        return {
            self.display.name: self.display.to_dict(),
            self.editor.name: self.editor.to_dict(),
            self.storage.name: self.storage.to_dict(),
            self.note.name: self.note.to_dict(),
            self.tag.name: self.tag.to_dict(),
            self.notebook.name: self.notebook.to_dict(),
        }


class DisplayDefaults(Defaults):
    # Configurable settings for `textwrap` module.
    width = 80
    max_lines = 5
    tabsize = 4
    replace_whitespace = False
    drop_whitespace = True
    placeholder = '...'
    initial_indent = '    '
    subsequent_indent = '    '

    # Pager
    default_pager = 'less'
    pager = ''


class DisplayConfig(ConfigBase):
    name = 'display'
    keys = [
        'width', 'max_lines', 'tabsize', 'replace_whitespace', 'drop_whitespace',
        'placeholder', 'initial_indent', 'subsequent_indent', 'pager',
    ]

    def __init__(self, **kwargs):
        super(DisplayConfig, self).__init__()
        for k in self.keys:
            setattr(self, k, kwargs.pop(k, getattr(DisplayDefaults, k)))

        # Detect pager only when it's not defined yet
        if self.pager == '':
            from shutil import which
            import platform

            if which(DisplayDefaults.default_pager) is not None:
                self.pager = DisplayDefaults.default_pager

            if self.pager == '' and platform.system() == 'Windows':
                if which('more') is not None:
                    self.pager = 'more'     # should be a builtin app on Windows

        self._check_remaining_kwargs(**kwargs)


class EditorDefaults(Defaults):
    executable = 'vim'
    fn_tempfile = osp.join(AppDefaults.dir_config, 'note.tmp')


class EditorConfig(ConfigBase):
    name = 'editor'
    keys = ['executable']

    def __init__(self, **kwargs):
        super(EditorConfig, self).__init__()
        self.executable = kwargs.pop('executable', EditorDefaults.executable)
        self.fn_tempfile = kwargs.pop('tempfile', EditorDefaults.fn_tempfile)
        self._check_remaining_kwargs(**kwargs)


class StorageDefaults(Defaults):
    valid_types = ['sqlite']
    type = 'sqlite'
    dir_root = osp.join(AppDefaults.dir_config, 'storage')


class StorageConfig(ConfigBase):
    name = 'storage'
    keys = ['type', 'dir_root']

    def __init__(self, **kwargs):
        super(StorageConfig, self).__init__()
        self.type = kwargs.pop('type', StorageDefaults.type)
        if self.type not in StorageDefaults.valid_types:
            raise ValueError('Type of storage "%s" is not supported, possible'
                ' choices: %s' % (self.type, StorageDefaults.valid_types))
        self.dir_root = kwargs.pop('dir_root', StorageDefaults.dir_root)
        self._check_remaining_kwargs(**kwargs)


class NoteDefaults(Defaults):
    max_title_len = 256


class NoteConfig(ConfigBase):
    name = 'note'
    keys = []

    def __init__(self, **kwargs):
        super(NoteConfig, self).__init__()
        self.max_title_len = NoteDefaults.max_title_len
        self._check_remaining_kwargs(**kwargs)


class TagDefaults(Defaults):
    """
    auto_parse : bool
        **For interactive mode only.**
        Automatically parsing content and create tags from it. If this feature
        is enabled, parsed tags will be pre-written in to the temporary file
        for editing tags (second stage of adding note).
    auto_remove_from_content : bool
        **For interactive mode only.**
        Remove parsed tags from note content. Note that this feature only works
        when `auto_parse` is True.
    """
    auto_parse = True
    auto_remove_from_content = True


class TagConfig(ConfigBase):
    name = 'tag'
    keys = ['auto_parse', 'auto_remove_from_content']

    def __init__(self, **kwargs):
        super(TagConfig, self).__init__()
        self.auto_parse = kwargs.pop('auto_parse', TagDefaults.auto_parse)
        self.auto_remove_from_content = kwargs.pop(
            'auto_remove_from_content', TagDefaults.auto_remove_from_content
        )
        self._check_remaining_kwargs(**kwargs)


class NotebookDefaults(Defaults):
    """
    fn_head : str
        A file contains information of current opening notebook. (like the
        meaing of `HEAD` in git)
    name_default : str
        Default name of the notebook that `HEAD` pointing. And it is also the
        first notebook created when this application is launched for the first
        time. Therefore, all notes will be saved into this notebook if there
        is no other notebooks created and opened.
    name_trash : str
        Name of the special notebook collecting removed notes.
    status_n_limit : int
        Limit of number of notes would be displayed while command
        `qnote status` is executed.
    """
    fn_head = osp.join(AppDefaults.dir_config, 'HEAD')
    name_default = '[DEFAULT]'
    name_trash = '[TRASH]'
    status_n_limit = 5


class NotebookConfig(ConfigBase):
    name = 'notebook'
    keys = []

    def __init__(self, **kwargs):
        super(NotebookConfig, self).__init__()
        self.fn_head = NotebookDefaults.fn_head
        self.name_default = NotebookDefaults.name_default
        self.name_trash = NotebookDefaults.name_trash
        self.status_n_limit = NotebookDefaults.status_n_limit
        self._check_remaining_kwargs(**kwargs)
