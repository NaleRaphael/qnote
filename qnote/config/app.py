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
    dir_config = osp.join(dir_home, '/.qnote')
    fn_config = osp.join(dir_config, 'config.json')


class AppConfig(ConfigBase):
    def __init__(self, **kwargs):
        super(AppConfig, self).__init__()
        if kwargs is None:
            kwargs = {}     # first initialization
        self.editor = EditorConfig(**kwargs.get('editor', {}))

    @classmethod
    def load(cls):
        with open(AppDefaults.fn_config, 'r') as f:
            content = json.load(f)
        return cls(**content)

    def write(self):
        os.makedirs(AppDefaults.dir_config)
        with open(AppDefaults.fn_config, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def to_dict(self):
        return {
            'editor': self.editor.to_dict(),
        }


class EditorDefaults(Defaults):
    executable = 'vim'


class EditorConfig(ConfigBase):
    def __init__(self, **kwargs):
        super(EditorConfig, self).__init__()
        self.executable = kwargs.get('executable', EditorDefaults.executable)

    def to_dict(self):
        keys = ['executable']
        return {k: getattr(self, k) for k in keys}
