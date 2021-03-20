from connect.reports.datamodels import RendererDefinition
from connect.reports.renderers import Jinja2Renderer

import pytest

from datetime import datetime
import json
from zipfile import ZipFile
import csv
from io import TextIOWrapper

from fs.tempfs import TempFS


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
        '(must be in the form <name>.<ext>.j2).',
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
    mocked_tmpdir = mocker.patch('connect.reports.renderers.j2.tempfile.TemporaryDirectory')
    mocked_zipfile = mocker.patch('connect.reports.renderers.j2.zipfile.ZipFile')
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

    assert renderer.render(data, 'report') == 'report.zip'
    if extra_context:
        assert 'name' in ctx['extra_context']
        assert 'desc' in ctx['extra_context']

    mocked_loader.assert_called_once_with('root_dir/report_root')
    mocked_environment.assert_called_once_with(loader=fsloader)
    env.get_template.assert_called_once_with('template.csv.j2')
    template_mock.stream.assert_called_once_with(ctx)
    stream_mock.dump.assert_called_once()
    assert mocked_open.mock_calls[0].args[0].rsplit('/', 1)[1] == 'report.csv'
    assert mocked_open.mock_calls[0].args[1] == 'w'
    assert mocked_zipfile.call_count == 1
    assert mocked_tmpdir.call_count == 1


def test_validate_tempfs_ok():
    tmp_fs = TempFS()
    tmplate_filename = 'template.csv.j2'
    tmp_fs.create(tmplate_filename)

    defs = RendererDefinition(
        root_path=tmp_fs.root_path,
        id='renderer_id',
        type='jinja2',
        description='description',
        template=tmplate_filename,
    )

    assert Jinja2Renderer.validate(defs) == []


def test_validate_tempfs_template_invalid_name():
    tmp_fs = TempFS()
    tmplate_filename = 'template.j3'
    tmp_fs.create(tmplate_filename)

    defs = RendererDefinition(
        root_path=tmp_fs.root_path,
        id='renderer_id',
        type='jinja2',
        description='description',
        template=tmplate_filename,
    )

    assert Jinja2Renderer.validate(defs) == [
        f'invalid template name: `{tmplate_filename}` '
        '(must be in the form <name>.<ext>.j2).',
    ]


def test_render_tempfs_ok(report_data, account_factory, report_factory):
    tmp_fs = TempFS()
    template_filename = 'template.csv.j2'
    directory_structure = 'package/report'
    tmp_fs.makedirs(directory_structure)
    path_to_template = f'{tmp_fs.root_path}/{directory_structure}/{template_filename}'
    with open(path_to_template, 'w') as fp:
        fp.write('"name";"description"\n')
        fp.write('{% for item in data %}')
        fp.write('"{{item[0]}}";"{{item[1]}}"\n')
        fp.write('{% endfor %}')
    account = account_factory()
    report = report_factory()
    renderer = Jinja2Renderer(
        'runtime', tmp_fs.root_path, account, report,
        f'{directory_structure}/{template_filename}',
    )

    # report_data method generates a matrix with this aspect:
    # [['row_0_col_0', 'row_0_col_1'], ['row_1_col_0', 'row_1_col_1']]
    data = report_data(2, 2)
    path_to_output_file = f'{tmp_fs.root_path}/{directory_structure}/report'
    output_file = renderer.render(data, path_to_output_file)

    with ZipFile(output_file) as repzip:
        assert sorted(repzip.namelist()) == ['report.csv', 'summary.json']
        with TextIOWrapper(repzip.open('report.csv'), encoding="utf-8") as fp:
            csv_reader = csv.reader(fp, delimiter=';')
            content = [row for row in csv_reader]

    assert output_file == f'{path_to_output_file}.zip'
    assert data[0] == content[1]
    assert data[1] == content[2]


def test_add_info_json(account_factory, report_factory):
    tmp_fs = TempFS()

    values = [{'param_id': 'param_value'}]
    report = report_factory(values=values)
    start_time = datetime.utcnow()

    renderer = Jinja2Renderer(
        'runtime',
        tmp_fs.root_path,
        account_factory(),
        report,
    )
    output_file = renderer._add_info_json(start_time, f'{tmp_fs.root_path}/summary.json')
    data = json.load(open(output_file, 'r'))

    assert output_file == f'{tmp_fs.root_path}/summary.json'
    assert data['data']['report_start_time'] == start_time.isoformat()
