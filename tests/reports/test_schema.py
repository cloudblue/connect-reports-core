import pytest

from connect.reports.validator import validate_with_schema


@pytest.mark.parametrize(
    ('renderer_type', 'template', 'args'),
    (
        ('json', None, None),
        ('xlsx', 'my_template.xlsx', {'start_row': 1, 'start_col': 1}),
    ),
)
def test_validation_schema(
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


def test_validation_schema_fail(repo_json, report_v1_json):
    report_v1 = report_v1_json()
    report_v1['report_spec'] = '5'
    repo = repo_json(report_v1)

    assert validate_with_schema(repo) is not None
