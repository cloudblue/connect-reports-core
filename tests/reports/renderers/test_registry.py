#  Copyright © 2022 CloudBlue. All rights reserved.

import pytest

from connect.reports.renderers.base import BaseRenderer
from connect.reports.renderers.registry import (
    RendererAlreadyRegisteredError,
    RendererNotFoundError,
    get_renderer,
    get_renderer_class,
    get_renderers,
    register,
)


def test_register(registry):
    @register('test')
    class TestRenderer(BaseRenderer):
        pass

    assert 'test' in registry
    assert registry['test'] == TestRenderer


def test_register_already_registered(registry):
    @register('test')
    class TestRenderer(BaseRenderer):
        pass

    with pytest.raises(RendererAlreadyRegisteredError):
        @register('test')
        class TestRenderer2(BaseRenderer):
            pass


def test_register_invalid_renderer(registry):
    with pytest.raises(ValueError):
        @register('test')
        class TestRenderer2:
            pass


def test_get_renderer_class(registry):
    @register('test')
    class TestRenderer(BaseRenderer):
        pass

    cls = get_renderer_class('test')
    assert cls == TestRenderer


def test_get_renderer_class_not_found(registry):
    with pytest.raises(RendererNotFoundError):
        get_renderer_class('test')


def test_get_renderer(registry, account_factory, report_factory):
    @register('test')
    class TestRenderer(BaseRenderer):

        def generate_report(self, data, output_file):
            pass

        async def generate_report_async(self, data, output_file):
            pass

    account = account_factory()
    report = report_factory()

    renderer = get_renderer(
        'test', 'runtime environment', 'root_dir',
        account, report, template='template.file', args={'a': 'b'},
    )

    assert isinstance(renderer, TestRenderer)
    assert renderer.environment == 'runtime environment'
    assert renderer.root_dir == 'root_dir'
    assert renderer.account == account
    assert renderer.report == report
    assert renderer.template == 'template.file'
    assert renderer.args == {'a': 'b'}


def test_renderers():
    @register('new_one')
    class NewRenderer(BaseRenderer):
        pass

    renderers = get_renderers()
    assert 'new_one' in renderers
