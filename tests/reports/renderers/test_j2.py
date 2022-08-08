#  Copyright © 2022 CloudBlue. All rights reserved.

from connect.reports.datamodels import RendererDefinition
from connect.reports.renderers import Jinja2Renderer

import pytest

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


@pytest.mark.parametrize(
    ('extra_context'),
    (
        {'name': 'test', 'desc': 'description'},
        None,
    ),
)
def test_render_tempfs_ok(report_data, account_factory, report_factory, extra_context):
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
    renderer.set_extra_context(extra_context)
    ctx = renderer.get_context(data)

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

    if extra_context:
        assert 'name' in ctx['extra_context']
        assert 'desc' in ctx['extra_context']


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('extra_context'),
    (
        {'name': 'test', 'desc': 'description'},
        None,
    ),
)
async def test_render_async_tempfs_ok(report_data, account_factory, report_factory, extra_context):
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
    renderer.set_extra_context(extra_context)
    ctx = renderer.get_context(data)

    path_to_output_file = f'{tmp_fs.root_path}/{directory_structure}/report'
    output_file = await renderer.render_async(data, path_to_output_file)

    with ZipFile(output_file) as repzip:
        assert sorted(repzip.namelist()) == ['report.csv', 'summary.json']
        with TextIOWrapper(repzip.open('report.csv'), encoding="utf-8") as fp:
            csv_reader = csv.reader(fp, delimiter=';')
            content = [row for row in csv_reader]

    assert output_file == f'{path_to_output_file}.zip'
    assert data[0] == content[1]
    assert data[1] == content[2]

    if extra_context:
        assert 'name' in ctx['extra_context']
        assert 'desc' in ctx['extra_context']
