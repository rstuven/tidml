import os
import six
from abc import ABCMeta


class Parameterized(object):
    """Abstract base class of parameterized classes."""

    __metaclass__ = ABCMeta

    def __init__(self, params={}):
        self.__params = params

    @property
    def params(self):
        return self.__params


def load_config(filepath):
    config = open(filepath, 'r').read()
    ext = os.path.splitext(filepath)[1]
    if ext == '.yaml':
        import yaml
        return yaml.load(config)
    elif ext == '.json':
        import json
        return json.loads(config)
    else:
        raise NotImplementedError('Not implemented config format ' + ext)


def prepare_path(filepath):
    """
    :param filepath:
    :rtype: str
    """
    filepath = os.path.expanduser(filepath)
    dirname = os.path.dirname(filepath)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return filepath


def init_spec(spec):
    """Instantiate a parameterized class using a specification.

    :param spec:
    """

    if not isinstance(spec, dict):
        # if not a dict, should be a class or a string
        ctor = spec
        params = {}
    else:
        # extract spec properties
        ctor = spec['class']
        params = spec.get('params', {})

    # load a class from string
    if isinstance(ctor, six.string_types):
        import importlib
        module_name, class_name = ctor.rsplit(".", 1)
        module = importlib.import_module(module_name)
        ctor = getattr(module, class_name)

    # validate type
    if not issubclass(ctor, Parameterized):
        raise RuntimeError("'{}' is not subclass of '{}'".format(
            ctor.__name__,
            Parameterized.__name__
        ))

    # now we're talking...
    instance = ctor(params)

    return instance


def extend(*args, **kwargs):
    def decorator(fn):
        name = kwargs.get('name', fn.__name__)
        for obj in args:
            if type(obj) == type:
                # extend class
                setattr(obj, name, fn)
            else:
                # extend instance
                import types
                m = types.MethodType(fn, obj, type(obj))
                setattr(type(obj), name, m)

        return fn

    return decorator


def require_argument(name, arg, the_type=None):
    if the_type is None:
        if arg is None:
            raise TypeError("Argument '{}' should have a value".format(name))
    elif type(arg) is not the_type:
        raise TypeError("Argument '{}' should be {}".format(name, the_type))
