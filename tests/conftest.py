import pytest

from connect.reports.datamodels import Account, Report


@pytest.fixture
def param_json():
    def _param_data(
        id='param_id', type='single_line',
        name='param name', description='param description',
        required=True, choices=None,
    ):
        data = {
            'id': id,
            'type': type,
            'name': name,
            'description': description,
            'required': required,
        }
        if choices is not None:
            data['choices'] = choices

        return data

    return _param_data


@pytest.fixture
def renderer_json():
    def _renderer_data(
        id='renderer_id', type='xlsx',
        description='XLSX renderer', template=None,
        kwargs=None,
    ):
        data = {
            'id': id,
            'type': type,
            'description': description,
        }
        if template is not None:
            data['template'] = template

        if kwargs is not None:
            data['kwargs'] = kwargs

        return data

    return _renderer_data


@pytest.fixture
def report_v2_json(param_json, renderer_json):
    def _report_data(
        name='Report',
        readme_file='path/to/readme.md',
        entrypoint='reports.report_package.entrypoint',
        audience=['vendor', 'provider'],  # noqa: B006
        parameters=[param_json()],  # noqa: B006
        renderers=[renderer_json()],  # noqa: B006
        default_renderer='renderer_id',
    ):

        data = {
            'name': name,
            'readme_file': readme_file,
            'entrypoint': entrypoint,
            'audience': audience,
            'parameters': parameters,
            'renderers': renderers,
            'report_spec': '2',
            'default_renderer': default_renderer,
        }

        return data

    return _report_data


@pytest.fixture
def report_v1_json(param_json):
    def _report_data(
        name='Report',
        readme_file='path/to/readme.md',
        entrypoint='reports.report_package.entrypoint',
        audience=['vendor', 'provider'],  # noqa: B006
        parameters=[param_json()],  # noqa: B006
        template='path/to/template.xlsx',
        start_row=1,
        start_col=1,
    ):

        data = {
            'name': name,
            'readme_file': readme_file,
            'entrypoint': entrypoint,
            'audience': audience,
            'parameters': parameters,
            'report_spec': '1',
            'template': template,
            'start_row': start_row,
            'start_col': start_col,
        }

        return data

    return _report_data


@pytest.fixture
def repo_json(report_v1_json, report_v2_json):
    def _repo_data(
        name='Reports Repository',
        readme_file='path/to/readme.md',
        version='1.0.0',
        language='python',
        reports=[report_v1_json(), report_v2_json()],  # noqa: B006
    ):

        return {
            'name': name,
            'readme_file': readme_file,
            'version': version,
            'language': language,
            'reports': reports,
        }

    return _repo_data


@pytest.fixture
def account_factory():
    def _account(id='VA-000', name='vendor account'):
        return Account(id=id, name=name)
    return _account


@pytest.fixture
def report_factory():
    def _report(
        id='report_id',
        name='report name',
        description='report description',
        values=[{'param_id': 'param_value'}],  # noqa: B006
    ):
        return Report(
            id=id,
            name=name,
            description=description,
            values=values,
        )

    return _report


@pytest.fixture
def report_data():
    def _data(rows=10, cols=10):
        return [
            [f'row_{i}_col_{j}' for j in range(cols)]
            for i in range(rows)
        ]
    return _data


@pytest.fixture
def registry(mocker):
    data = {}
    mocker.patch('connect.reports.renderers.registry._RENDERERS', data)
    return data
