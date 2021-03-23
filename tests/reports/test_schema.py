#  Copyright © 2021 CloudBlue. All rights reserved.

import pytest

from connect.reports.validator import validate_with_schema


@pytest.mark.parametrize(
    ('renderer_type', 'template', 'args'),
    (
        ('json', None, None),
        ('xlsx', 'my_template.xlsx', {'start_row': 1, 'start_col': 1}),
    ),
)
def test_schema_ok(
    repo_json, report_v1_json, report_v2_json, renderer_json,
    renderer_type, template, args,
):
    report_v1 = report_v1_json()
    report_v2 = report_v2_json(renderers=[
        renderer_json(
            type=renderer_type,
            description=f'{renderer_type.upper()} renderer.',
            template=template,
            args=args,
        ),
    ])
    repo = repo_json(reports=[report_v1, report_v2])

    assert validate_with_schema(repo) is None


@pytest.mark.parametrize(
    ('field'),
    ('name', 'readme_file', 'version', 'language', 'reports'),
)
def test_repo_object_required_fields(repo_json, field):
    repo = repo_json()
    repo.pop(field)
    errors = validate_with_schema(repo)

    assert errors is not None
    assert f"'{field}' is a required property" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('name', 'readme_file', 'version', 'language'),
)
def test_repo_object_field_types(repo_json, field):
    repo = repo_json()
    repo[field] = 1
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "1 is not of type 'string'" == errors.splitlines()[0]


def test_repo_object_reports_field(repo_json):
    repo = repo_json(reports='reports')
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "'reports' is not of type 'array'" == errors.splitlines()[0]


def test_repo_object_reports_minitem(repo_json):
    repo = repo_json(reports=[])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert '[] is too short' == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    (
        'name', 'readme_file', 'template', 'start_row',
        'start_col', 'entrypoint', 'audience', 'report_spec',
    ),
)
def test_reportv1_object_required_fields(repo_json, report_v1_json, field):
    report = report_v1_json()
    report.pop(field)
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert f"'{field}' is a required property" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('name', 'readme_file', 'template', 'entrypoint', 'report_spec'),
)
def test_reportv1_object_string_fields(repo_json, report_v1_json, field):
    report = report_v1_json()
    report[field] = 1
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "1 is not of type 'string'" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('start_row', 'start_col'),
)
def test_reportv1_object_number_fields(repo_json, report_v1_json, field):
    report = report_v1_json()
    report[field] = 'string'
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "'string' is not of type 'number'" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('audience', 'parameters'),
)
def test_reportv1_object_array_fields(repo_json, report_v1_json, field):
    report = report_v1_json()
    report[field] = 'string'
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "'string' is not of type 'array'" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('start_row', 'start_col'),
)
def test_reportv1_object_number_minimum(repo_json, report_v1_json, field):
    report = report_v1_json()
    report[field] = 0
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert '0 is less than the minimum of 1' == errors.splitlines()[0]


def test_reportv1_object_array_minitems_audience(repo_json, report_v1_json):
    report = report_v1_json(audience=[])
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert '[] is too short' == errors.splitlines()[0]


def test_reportv1_object_audience_string_items(repo_json, report_v1_json):
    report = report_v1_json(audience=[1])
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "1 is not of type 'string'" == errors.splitlines()[0]


def test_reportv1_object_report_spec(repo_json, report_v1_json):
    report = report_v1_json()
    report['report_spec'] = '5'
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "'5' is not one of ['1', '2']" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    (
        'name', 'readme_file', 'entrypoint', 'audience',
        'report_spec', 'renderers', 'default_renderer',
    ),
)
def test_reportv2_object_required_fields(repo_json, report_v2_json, field):
    report = report_v2_json()
    report.pop(field)
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert f"'{field}' is a required property" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('name', 'readme_file', 'entrypoint', 'report_spec', 'default_renderer'),
)
def test_reportv2_object_string_fields(repo_json, report_v2_json, field):
    report = report_v2_json()
    report[field] = 1
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "1 is not of type 'string'" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('audience', 'renderers', 'parameters'),
)
def test_reportv2_object_array_fields(repo_json, report_v2_json, field):
    report = report_v2_json()
    report[field] = 'string'
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "'string' is not of type 'array'" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('audience', 'renderers'),
)
def test_reportv2_object_array_minitems(repo_json, report_v2_json, field):
    report = report_v2_json()
    report[field] = []
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert '[] is too short' == errors.splitlines()[0]


def test_reportv2_object_audience_string_items(repo_json, report_v2_json):
    report = report_v2_json(audience=[1])
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "1 is not of type 'string'" == errors.splitlines()[0]


def test_reportv2_object_report_spec(repo_json, report_v2_json):
    report = report_v2_json()
    report['report_spec'] = '5'
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "'5' is not one of ['1', '2']" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('id', 'type', 'description'),
)
def test_renderer_object_required_fields(repo_json, report_v2_json, field):
    report = report_v2_json()
    report['renderers'][0].pop(field)
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert f"'{field}' is a required property" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('id', 'type', 'description', 'template'),
)
def test_renderer_object_string_fields(repo_json, report_v2_json, field):
    report = report_v2_json()
    report['renderers'][0][field] = 1
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "1 is not of type 'string'" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('id', 'type', 'name', 'description'),
)
def test_parameter_object_required_fields(repo_json, report_v2_json, field):
    report = report_v2_json()
    report['parameters'][0].pop(field)
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert f"'{field}' is a required property" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('id', 'type', 'name', 'description'),
)
def test_parameter_object_string_fields(repo_json, report_v2_json, field):
    report = report_v2_json()
    report['parameters'][0][field] = 1
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "1 is not of type 'string'" == errors.splitlines()[0]


def test_parameter_object_required_boolean_field(repo_json, report_v2_json):
    report = report_v2_json()
    report['parameters'][0]['required'] = 1
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "1 is not of type 'boolean'" == errors.splitlines()[0]


def test_parameter_object_choices_array_field(repo_json, report_v2_json):
    report = report_v2_json()
    report['parameters'][0]['choices'] = 1
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "1 is not of type 'array'" == errors.splitlines()[0]


def test_parameter_object_minitem_choices_field(repo_json, report_v2_json):
    report = report_v2_json()
    report['parameters'][0]['choices'] = []
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "[] is too short" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('value', 'label'),
)
def test_choice_object_required_fields(repo_json, report_v2_json, param_json, field):
    params = [param_json(
        choices=[
            {'value': 'v1', 'label': 'l1'},
        ],
    )]
    report = report_v2_json(parameters=params)
    report['parameters'][0]['choices'][0].pop(field)
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert f"'{field}' is a required property" == errors.splitlines()[0]


@pytest.mark.parametrize(
    ('field'),
    ('value', 'label'),
)
def test_choice_object_string_fields(param_json, repo_json, report_v2_json, field):
    params = [param_json(
        choices=[
            {'value': 'v1', 'label': 'l1'},
        ],
    )]
    report = report_v2_json(parameters=params)
    report['parameters'][0]['choices'][0][field] = 1
    repo = repo_json(reports=[report])
    errors = validate_with_schema(repo)

    assert errors is not None
    assert "1 is not of type 'string'" == errors.splitlines()[0]
