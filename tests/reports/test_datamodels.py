#  Copyright © 2022 CloudBlue. All rights reserved.

import os

import pytest
from fs.tempfs import TempFS

from connect.reports.datamodels import (
    ParameterDefinition,
    RendererDefinition,
    ReportDefinition,
    RepositoryDefinition,
)


@pytest.mark.parametrize(
    ('entrypoint', 'local_id'),
    (
        ('rootpkg.reportmodule.entrypoint', 'reportmodule'),
        ('rootpkg.reportmodule.anothermodule.entrypoint', 'reportmodule'),
        ('rootpkg.reportmodule', None),
        ('rootpkg', None),
    ),
)
def test_report_definition_local_id(report_v2_json, entrypoint, local_id):
    defs = ReportDefinition(root_path='root_path', **report_v2_json(entrypoint=entrypoint))
    assert defs.local_id == local_id


def test_report_definition_description(mocker, report_v2_json):
    report_json = report_v2_json()
    expected_descr = 'This is the report markdown description'

    expected_readme_path = os.path.join('root_path', report_json['readme_file'])

    mocked_open = mocker.mock_open(read_data=expected_descr)
    mocker.patch('connect.reports.datamodels.open', mocked_open)

    defs = ReportDefinition(root_path='root_path', **report_json)
    assert defs.description == expected_descr
    assert mocked_open.mock_calls[0].args == (expected_readme_path, 'r')


def test_report_definition_default_renderer(mocker, report_v2_json, renderer_json):
    report_json = report_v2_json(
        renderers=[RendererDefinition(root_path='root_path', **renderer_json())],
    )
    defs = ReportDefinition(root_path='root_path', **report_json)
    assert defs.default_renderer == defs.renderers[0].id


def test_report_get_parameters(mocker, report_v2_json, param_json):
    report_json = report_v2_json()
    param = param_json()
    report_json['parameters'] = [ParameterDefinition(**param)]

    defs = ReportDefinition(root_path='root_path', **report_json)
    assert defs.get_parameters() == [param]


def test_repository_definition_description(mocker, repo_json):
    repo_data = repo_json()

    expected_descr = 'This is the repository markdown description'
    expected_readme_path = os.path.join('root_path', repo_data['readme_file'])

    mocked_open = mocker.mock_open(read_data=expected_descr)
    mocker.patch('connect.reports.datamodels.open', mocked_open)

    defs = RepositoryDefinition(root_path='root_path', **repo_data)
    assert defs.description == expected_descr
    assert mocked_open.mock_calls[0].args == (expected_readme_path, 'r')


def test_report_tempfs_definition_description(report_v2_json):
    expected_descr = 'This is the report markdown description'
    tmp_fs = TempFS()
    with tmp_fs.open('readme.md', 'w') as fp:
        fp.write(expected_descr)

    report_json = report_v2_json(readme_file='readme.md')
    defs = ReportDefinition(root_path=tmp_fs.root_path, **report_json)

    assert defs.description == expected_descr


def test_repository_tempfs_definition_description(repo_json):
    expected_descr = 'This is the repository markdown description'
    tmp_fs = TempFS()
    with tmp_fs.open('readme.md', 'w') as fp:
        fp.write(expected_descr)

    repo_data = repo_json(readme_file='readme.md')
    defs = RepositoryDefinition(root_path=tmp_fs.root_path, **repo_data)

    assert defs.description == expected_descr


def test_report_get_renderers(mocker, report_v2_json, renderer_json):
    report_json = report_v2_json()
    renderer = RendererDefinition(root_path='root_path', **renderer_json())
    report_json['renderers'] = [renderer]
    defs = ReportDefinition(root_path='root_path', **report_json)

    data = defs.get_renderers()

    assert data[0]['id'] == renderer.id
    assert data[0]['type'] == renderer.type
    assert data[0]['description'] == renderer.description
    assert 'root_path' not in data[0]


def test_report_get_renderers_multiple(mocker, report_v2_json, renderer_json):
    report_json = report_v2_json()
    xls_renderer = RendererDefinition(
        root_path='root_path',
        **renderer_json(id='xlsx_renderer', default=False),
    )
    json_renderer = RendererDefinition(
        root_path='root_path',
        **renderer_json(
            id='json_renderer',
            type='json',
            default=True,
            description='Json renderer',
        ),
    )
    csv_renderer = RendererDefinition(
        root_path='root_path',
        **renderer_json(
            id='csv_renderer',
            type='csv',
            default=False,
            description='Csv renderer',
        ),
    )
    pdf_renderer = RendererDefinition(
        root_path='root_path',
        **renderer_json(
            id='pdf_renderer',
            type='pdf',
            default=False,
            description='Pdf renderer',
            template='template.j2',
            args={'key1': 'value1', 'key2': 'value2'},
        ),
    )
    report_json['renderers'] = [xls_renderer, json_renderer, csv_renderer, pdf_renderer]
    defs = ReportDefinition(root_path='root_path', **report_json)

    data = defs.get_renderers()

    assert isinstance(data, list)
    assert len(data) == 4
    assert data[0]['id'] == 'xlsx_renderer'

    for renderer in data:
        if renderer['default']:
            assert renderer['id'] == 'json_renderer'
