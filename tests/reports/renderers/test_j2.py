from connect.reports.datamodels import RendererDefinition
from connect.reports.renderers import Jinja2Renderer

import pytest


def test_validate_ok(mocker):
    mocker.patch('connect.reports.renderers.j2.os.path.isfile', return_value=True)

    defs = RendererDefinition(
        root_path='root_path',
        id='renderer_id',
        type='jinja2',
        description='description',
        template='template.csv.j2',
    )

    assert Jinja2Renderer.validate(defs) == []


def test_validate_no_template():
    defs = RendererDefinition(
        root_path='root_path',
        id='renderer_id',
        type='jinja2',
        description='description',
    )

    assert Jinja2Renderer.validate(defs) == ['`template` is required for jinja2 renderer.']


def test_validate_template_not_found(mocker):
    mocker.patch('connect.reports.renderers.j2.os.path.isfile', return_value=False)
    defs = RendererDefinition(
        root_path='root_path',
        id='renderer_id',
        type='jinja2',
        description='description',
        template='template.csv.j2',
    )

    assert Jinja2Renderer.validate(defs) == ['template `template.csv.j2` not found.']


def test_validate_template_invalid_name(mocker):
    mocker.patch('connect.reports.renderers.j2.os.path.isfile', return_value=True)
    defs = RendererDefinition(
        root_path='root_path',
        id='renderer_id',
        type='jinja2',
        description='description',
        template='template.j3',
    )

    assert Jinja2Renderer.validate(defs) == [
        'invalid template name: `template.j3` '
        '(must be in the form <name>.<ext>.j2 or <name>.j2).',
    ]


@pytest.mark.parametrize(
    ('extra_context'),
    (
        {'name': 'test', 'desc': 'description'},
        None,
    ),
)
def test_render(mocker, account_factory, report_factory, report_data, extra_context):
    account = account_factory()
    report = report_factory()
    fsloader = mocker.MagicMock()
    stream_mock = mocker.MagicMock()
    template_mock = mocker.MagicMock()
    template_mock.stream.return_value = stream_mock
    env = mocker.MagicMock()
    env.get_template.return_value = template_mock
    mocked_open = mocker.mock_open()
    mocker.patch('connect.reports.renderers.j2.open', mocked_open)
    mocked_loader = mocker.patch(
        'connect.reports.renderers.j2.FileSystemLoader',
        return_value=fsloader,
    )
    mocked_environment = mocker.patch(
        'connect.reports.renderers.j2.Environment',
        return_value=env,
    )

    renderer = Jinja2Renderer(
        'runtime environment', 'root_dir', account, report,
        'report_root/template.csv.j2',
    )

    data = report_data()
    renderer.set_extra_context(extra_context)
    ctx = renderer.get_context(data)

    assert renderer.render(data, 'report') == 'report.csv'
    if extra_context:
        assert 'name' in ctx['extra_context']
        assert 'desc' in ctx['extra_context']

    mocked_loader.assert_called_once_with('root_dir/report_root')
    mocked_environment.assert_called_once_with(loader=fsloader)
    env.get_template.assert_called_once_with('template.csv.j2')
    template_mock.stream.assert_called_once_with(ctx)
    stream_mock.dump.assert_called_once()
    assert mocked_open.mock_calls[0].args == ('report.csv', 'w')
