import os.path as osp
import importlib.util

from .base import BaseStorer


__all__ = ['get_storer']


def get_storer(config):
    """Dynamically import storer to avoid unnecessary bytecode compilation,
    external dependencies, or even database initialization of other storage
    implementation.

    Parameters
    ----------
    config : `qnote.config.AppConfig`

    Returns
    -------
    storer : an instance of a subclass from `qnote.storage.BaseStorer`
    """
    _type = config.storage.type
    this_dir = osp.dirname(__file__)
    fn = osp.join(this_dir, _type, 'storer.py')
    module_name = 'qnote.storage.%s.storer' % _type

    spec = importlib.util.spec_from_file_location(module_name, fn)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    storer_name = getattr(mod, 'STORER_IMPL', None)
    if storer_name is None:
        candiates = [v for v in dir(mod) if (
            v.endswith('Storer') and v != 'BaseStorer'
        )]
        assert len(candiates) == 1, (
            'Failed to find valid storer class, this might be an '
            'implementation error.'
        )
        cls_storer = getattr(mod, candiates[0])
    else:
        cls_storer = getattr(mod, storer_name)

    storer = cls_storer(config)
    assert isinstance(storer, BaseStorer), (
        'Type of imported `storer` should be a subclass of %s, this might '
        'be an implementation error.' % BaseStorer
    )
    return storer
