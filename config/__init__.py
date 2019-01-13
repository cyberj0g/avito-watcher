import datetime
import os
import sys
import types

import config.settings

# create config object corresponding to specified env
ENV = os.environ.get('ENV', 'Base')
_current = getattr(sys.modules['config.settings'], '{0}Config'.format(ENV))()


def set_attrs():
    # copy attributes to the module for convenience
    for atr in [f for f in dir(_current) if '__' not in f]:
        # environment can override anything
        val = os.environ.get(atr, getattr(_current, atr))
        setattr(sys.modules[__name__], atr, val)


set_attrs()


def as_dict():
    res = {}
    for atr in [f for f in dir(config) if (('__' not in f) and (not f.startswith('_')))]:
        val = getattr(config, atr)
        if all(map(lambda x: not isinstance(val, x), [types.ModuleType, types.FunctionType])):
            res[atr] = val
    return res
