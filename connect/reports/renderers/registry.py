#  Copyright © 2021 CloudBlue. All rights reserved.

from connect.reports.renderers.base import BaseRenderer

_RENDERERS = {}


class RendererAlreadyRegisteredError(Exception):
    pass


class RendererNotFoundError(Exception):
    pass


def register(name):
    if name in _RENDERERS:
        raise RendererAlreadyRegisteredError(f'The renderer {name} is already registered.')

    def _wrapper(cls):
        if not issubclass(cls, BaseRenderer):
            raise ValueError('The provided class must be a subclass of BaseRenderer.')

        _RENDERERS[name] = cls

        return cls
    return _wrapper


def get_renderer_class(name):
    if name not in _RENDERERS:
        raise RendererNotFoundError(f'The renderer {name} does not exist.')
    return _RENDERERS[name]


def get_renderer(name, environment, project_dir, account, report, template=None, args=None):
    cls = get_renderer_class(name)
    return cls(environment, project_dir, account, report, template, args)


def get_renderers():
    return _RENDERERS.keys()
