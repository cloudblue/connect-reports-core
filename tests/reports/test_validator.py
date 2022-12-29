#  Copyright © 2022 CloudBlue. All rights reserved.

import pytest
from fs.tempfs import TempFS

from connect.reports.datamodels import (
    ChoicesParameterDefinition,
    ParameterDefinition,
    RendererDefinition,
    ReportDefinition,
    RepositoryDefinition,
)
from connect.reports.validator import (
    _validate_parameters,
    _validate_renderer,
    _validate_report,
    validate,
)


def test_validator_parameters_unknown_type(param_json):
    param_ok = param_json()
    param_ko = param_json(type='wrong')

    parameters = [
        ParameterDefinition(**param_ok),
        ParameterDefinition(**param_ko),
    ]
    errors = _validate_parameters('report_one', parameters)

    assert len(errors) != 0
    assert 'Invalid type' in errors[0]
    assert 'report_one' in errors[0]


def test_validator_parameters_choice_type_with_no_choice(param_json):
    param = param_json(type='choice', choices=[])

    parameters = [ChoicesParameterDefinition(**param)]
    errors = _validate_parameters('report_one', parameters)

    assert len(errors) != 0
    assert 'Missing choices' in errors[0]
    assert 'report_one' in errors[0]


@pytest.mark.parametrize(
    ('renderer_type'),
    ('wrong', 'json'),
)
def test_validator_renderer_unknown_type(param_json, renderer_type):
    report_dict = {
        'name': 'Report',
        'readme_file': 'readme.md',
        'entrypoint': 'reports.report_package.entrypoint',
        'audience': ['vendor', 'provider'],
        'parameters': [param_json()],
        'report_spec': '2',
    }

    tmp_fs = _get_tmpfs_with_readme_and_entry(report_dict['entrypoint'])

    renderer_dict = {
        'root_path': tmp_fs.root_path,
        'id': '123',
        'type': renderer_type,
        'default': True,
        'description': 'Renderer',
    }
    renderer = RendererDefinition(**renderer_dict)

    errors = _validate_renderer('report_one', renderer)
    if renderer_type == 'json':
        assert len(errors) == 0
    else:
        assert len(errors) != 0
        assert 'not known' in errors[0]
        assert 'report_one' in errors[0]


def test_validator_readme_file_not_existing(report_v2_json, param_json):
    renderer_json_dict = {
        'root_path': 'root_path',
        'id': '321',
        'type': 'json',
        'description': 'JSON Renderer',
        'default': True,
    }
    renderer = RendererDefinition(**renderer_json_dict)
    parameter = ParameterDefinition(**param_json())
    report_dict = report_v2_json(renderers=[renderer], parameters=[parameter])
    report = ReportDefinition(
        root_path='root_path',
        **report_dict,
    )
    errors = _validate_report(report)

    assert len(errors) != 0
    assert 'property `readme_file` cannot be resolved' in errors[0]


def test_validator_entrypoint_bad_format(report_v2_json):
    tmp_filesystem = TempFS()
    tmp_filesystem.create('readme.md')
    renderer_json_dict = {
        'root_path': tmp_filesystem.root_path,
        'id': '321',
        'type': 'json',
        'description': 'JSON Renderer',
    }
    renderer = RendererDefinition(**renderer_json_dict)
    report_dict = report_v2_json(
        readme_file='readme.md',
        entrypoint='mypackage',
        renderers=[renderer],
    )
    report = ReportDefinition(
        root_path=tmp_filesystem.root_path,
        **report_dict,
    )
    errors = _validate_report(report)

    assert len(errors) != 0
    assert 'does not follow the package structure' in errors[0]


def test_validator_entrypoint_bad_directory_structure(report_v2_json, param_json):
    tmp_filesystem = TempFS()
    tmp_filesystem.create('readme.md')
    renderer_json_dict = {
        'root_path': tmp_filesystem.root_path,
        'id': '321',
        'type': 'json',
        'description': 'JSON Renderer',
        'default': True,
    }
    renderer = RendererDefinition(**renderer_json_dict)
    parameter = ParameterDefinition(**param_json())
    report_dict = report_v2_json(
        readme_file='readme.md',
        renderers=[renderer],
        parameters=[parameter],
    )
    report = ReportDefinition(
        root_path=tmp_filesystem.root_path,
        **report_dict,
    )
    errors = _validate_report(report)

    assert len(errors) != 0
    assert 'directory structure does not match' in errors[0]


def test_validator_duplicate_renderers_error(param_json):
    report_dict = {
        'name': 'Report',
        'readme_file': 'readme.md',
        'entrypoint': 'reports.report_package.entrypoint',
        'audience': ['vendor', 'provider'],
        'report_spec': '2',
    }

    tmp_fs = _get_tmpfs_with_readme_and_entry(report_dict['entrypoint'])

    renderer_dict = {
        'root_path': tmp_fs.root_path,
        'id': '123',
        'type': 'csv',
        'description': 'CSV Renderer',
        'default': True,
    }
    renderer = RendererDefinition(**renderer_dict)
    parameter = ParameterDefinition(**param_json())
    report = ReportDefinition(
        root_path=tmp_fs.root_path,
        **report_dict,
        renderers=[renderer, renderer],
        parameters=[parameter],
    )
    errors = _validate_report(report)

    assert len(errors) != 0
    assert 'duplicated renderer' in errors[0]


def test_validator_ok(param_json):
    report_dict = {
        'name': 'Report',
        'readme_file': 'readme.md',
        'entrypoint': 'reports.report_package.entrypoint',
        'audience': ['vendor', 'provider'],
        'report_spec': '2',
    }

    tmp_fs = _get_tmpfs_with_readme_and_entry(report_dict['entrypoint'])

    renderer_csv_dict = {
        'root_path': tmp_fs.root_path,
        'id': '123',
        'type': 'csv',
        'description': 'CSV Renderer',
        'default': True,
    }
    csv_renderer = RendererDefinition(**renderer_csv_dict)
    parameter = ParameterDefinition(**param_json())
    report = ReportDefinition(
        root_path=tmp_fs.root_path,
        **report_dict,
        renderers=[csv_renderer],
        parameters=[parameter],
    )
    errors = _validate_report(report)
    assert len(errors) == 0


def test_validator_multiple_default_renderer(param_json):
    report_dict = {
        'name': 'Report',
        'readme_file': 'readme.md',
        'entrypoint': 'reports.report_package.entrypoint',
        'audience': ['vendor', 'provider'],
        'report_spec': '2',
    }

    tmp_fs = _get_tmpfs_with_readme_and_entry(report_dict['entrypoint'])

    renderer_json_dict = {
        'root_path': tmp_fs.root_path,
        'id': '321',
        'type': 'json',
        'description': 'JSON Renderer',
        'default': True,
    }
    renderer_csv_dict = {
        'root_path': tmp_fs.root_path,
        'id': '123',
        'type': 'csv',
        'description': 'CSV Renderer',
        'default': True,
    }
    csv_renderer = RendererDefinition(**renderer_csv_dict)
    json_renderer = RendererDefinition(**renderer_json_dict)
    parameter = ParameterDefinition(**param_json())
    report = ReportDefinition(
        root_path=tmp_fs.root_path,
        **report_dict,
        renderers=[csv_renderer, json_renderer],
        parameters=[parameter],
    )
    errors = _validate_report(report)
    assert len(errors) != 0
    assert f'report {report.local_id} has multiple default renderers:' in errors[0]


def test_validator_repo_readme_file_missing(param_json):
    report_dict = {
        'name': 'Report',
        'readme_file': 'readme.md',
        'entrypoint': 'reports.report_package.entrypoint',
        'audience': ['vendor', 'provider'],
        'report_spec': '2',
    }
    renderer_csv_dict = {
        'root_path': 'root_path',
        'id': '123',
        'type': 'csv',
        'description': 'CSV Renderer',
        'default': True,
    }
    csv_renderer = RendererDefinition(**renderer_csv_dict)
    parameter = ParameterDefinition(**param_json())
    report = ReportDefinition(
        root_path='root_path',
        **report_dict,
        renderers=[csv_renderer],
        parameters=[parameter],
    )
    repo_dict = {
        'name': 'Reports Repository',
        'readme_file': 'readme.md',
        'version': '1.0.0',
        'language': 'python',
        'reports': [report],
    }
    repo = RepositoryDefinition(root_path='root_path', **repo_dict)
    errors = validate(repo)

    assert len(errors) != 0
    assert 'repository property `readme_file` cannot be resolved' in errors[0]


def test_validator_repo_duplicated_reports(mocker, param_json):
    mocker.patch(
        'connect.reports.validator._validate_report',
        return_value=[],
    )
    report_dict_1 = {
        'name': 'Report',
        'readme_file': 'readme.md',
        'entrypoint': 'reports.report_package.entrypoint',
        'audience': ['vendor', 'provider'],
        'parameters': [param_json()],
        'report_spec': '2',
    }
    report_dict_2 = {
        'name': 'Report',
        'readme_file': 'readme.md',
        'entrypoint': 'reports.report_package.entrypoint',
        'audience': ['vendor', 'provider'],
        'parameters': [param_json()],
        'report_spec': '2',
    }
    renderer_csv_dict = {
        'root_path': 'root_path',
        'id': '123',
        'type': 'csv',
        'description': 'CSV Renderer',
        'default': True,
    }
    csv_renderer = RendererDefinition(**renderer_csv_dict)
    report_1 = ReportDefinition(
        root_path='root_path',
        **report_dict_1,
        renderers=[csv_renderer],
    )
    report_2 = ReportDefinition(
        root_path='root_path',
        **report_dict_2,
        renderers=[csv_renderer],
    )
    tmp_filesystem = TempFS()
    tmp_filesystem.create('readme.md')
    repo_dict = {
        'name': 'Reports Repository',
        'readme_file': 'readme.md',
        'version': '1.0.0',
        'language': 'python',
        'reports': [report_1, report_2],
    }
    repo = RepositoryDefinition(
        root_path=tmp_filesystem.root_path,
        **repo_dict,
    )

    errors = validate(repo)

    assert len(errors) != 0
    assert 'Multiple reports within single module found' in errors[0]


def test_validator_duplicate_parameters_error(param_json):
    report_dict = {
        'name': 'Report',
        'readme_file': 'readme.md',
        'entrypoint': 'reports.report_package.entrypoint',
        'audience': ['vendor', 'provider'],
        'report_spec': '2',
    }
    tmp_fs = _get_tmpfs_with_readme_and_entry(report_dict['entrypoint'])

    renderer_csv_dict = {
        'root_path': tmp_fs.root_path,
        'id': '123',
        'type': 'csv',
        'description': 'CSV Renderer',
        'default': True,
    }
    csv_renderer = RendererDefinition(**renderer_csv_dict)
    parameter = ParameterDefinition(**param_json())
    report = ReportDefinition(
        root_path=tmp_fs.root_path,
        **report_dict,
        parameters=[parameter, parameter],
        renderers=[csv_renderer],
    )
    errors = _validate_report(report)

    assert len(errors) != 0
    assert 'parameter ids are duplicated' in errors[0]


def test_validator_empty_parameter_list(param_json):
    report_dict = {
        'name': 'Report',
        'readme_file': 'readme.md',
        'entrypoint': 'reports.report_package.entrypoint',
        'audience': ['vendor', 'provider'],
        'report_spec': '2',
    }
    tmp_fs = _get_tmpfs_with_readme_and_entry(report_dict['entrypoint'])
    renderer_csv_dict = {
        'root_path': tmp_fs.root_path,
        'id': '123',
        'type': 'csv',
        'description': 'CSV Renderer',
        'default': True,
    }
    csv_renderer = RendererDefinition(**renderer_csv_dict)
    report = ReportDefinition(
        root_path=tmp_fs.root_path,
        **report_dict,
        parameters=[],
        renderers=[csv_renderer],
    )
    errors = _validate_report(report)

    assert len(errors) == 0


def _get_tmpfs_with_readme_and_entry(entrypoint):
    tmp_fs = TempFS()
    tmp_fs.create('readme.md')

    *dirpath, filename = entrypoint.split('.')
    package_path = '/'.join(dirpath)
    script_path = f'{package_path}/{filename}.py'
    tmp_fs.makedirs(package_path)
    tmp_fs.create(script_path)

    return tmp_fs
