import os
import os.path as osp
import json


__all__ = ['AppConfig']


class Defaults(object):
    pass


class ConfigBase(object):
    def __init__(self):
        pass

    def to_dict(self):
        raise NotImplementedError


class AppDefaults(Defaults):
    dir_home = os.getenv('HOME', osp.expanduser('~'))
    dir_config = osp.join(dir_home, '.qnote')
    fn_config = osp.join(dir_config, 'config.json')


class AppConfig(ConfigBase):
    def __init__(self, **kwargs):
        super(AppConfig, self).__init__()
        if kwargs is None:
            kwargs = {}     # first initialization
        self.editor = EditorConfig(**kwargs.pop('editor', {}))
        self.storage = StorageConfig(**kwargs.pop('storage', {}))
        self.tag = TagConfig(**kwargs.pop('tag', {}))

        # Check whether there are remaining values for configuration
        if len(kwargs) != 0:
            import warnings
            msg = (
                f'There are unknown configuration values, did you added them'
                'by accident? {kwargs}'
            )
            warnings.warn(msg, RuntimeWarning)

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
            return cls(**content)

    def write(self):
        os.makedirs(AppDefaults.dir_config, exist_ok=True)
        with open(AppDefaults.fn_config, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def to_dict(self):
        return {
            'editor': self.editor.to_dict(),
            'storage': self.storage.to_dict(),
            'tag': self.tag.to_dict(),
        }


class EditorDefaults(Defaults):
    executable = 'vim'
    fn_tempfile = osp.join(AppDefaults.dir_config, 'note.tmp')


class EditorConfig(ConfigBase):
    def __init__(self, **kwargs):
        super(EditorConfig, self).__init__()
        self.executable = kwargs.get('executable', EditorDefaults.executable)
        self.fn_tempfile = kwargs.get('tempfile', EditorDefaults.fn_tempfile)

    def to_dict(self):
        keys = ['executable']
        return {k: getattr(self, k) for k in keys}


class StorageDefaults(Defaults):
    valid_types = ['sqlite']
    type = 'sqlite'
    dir_root = osp.join(AppDefaults.dir_config, 'storage')


class StorageConfig(ConfigBase):
    def __init__(self, **kwargs):
        super(StorageConfig, self).__init__()
        self.type = kwargs.get('type', StorageDefaults.type)
        if self.type not in StorageDefaults.valid_types:
            raise ValueError('Type of storage "%s" is not supported, possible'
                ' choices: %s' % (self.type, StorageDefaults.valid_types))
        self.dir_root = kwargs.get('dir_root', StorageDefaults.dir_root)

    def to_dict(self):
        keys = ['type', 'dir_root']
        return {k: getattr(self, k) for k in keys}


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
    def __init__(self, **kwargs):
        super(TagConfig, self).__init__()
        self.auto_parse = kwargs.get('auto_parse', TagDefaults.auto_parse)
        self.auto_remove_from_content = kwargs.get(
            'auto_remove_from_content', TagDefaults.auto_remove_from_content
        )

    def to_dict(self):
        keys = ['auto_parse', 'auto_remove_from_content']
        return {k: getattr(self, k) for k in keys}
