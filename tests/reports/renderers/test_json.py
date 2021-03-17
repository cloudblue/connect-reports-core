from connect.reports.datamodels import RendererDefinition
from connect.reports.renderers import JSONRenderer

from fs.tempfs import TempFS

import json


def test_validate_ok():

    defs = RendererDefinition(
        root_path='root_path',
        id='renderer_id',
        type='json',
        description='description',
    )

    assert JSONRenderer.validate(defs) == []


def test_render(mocker, account_factory, report_factory, report_data):
    mocked_open = mocker.mock_open()
    mocker.patch('connect.reports.renderers.json.open', mocked_open)
    mocked_dump = mocker.patch(
        'connect.reports.renderers.json.json.dump',
    )

    data = report_data()

    renderer = JSONRenderer(
        'runtime environment',
        'root_dir',
        account_factory(),
        report_factory(),
    )

    assert renderer.render(data, 'report') == 'report.json'
    assert mocked_dump.mock_calls[0].args[0] == data
    assert mocked_open.mock_calls[0].args == ('report.json', 'w')


def test_render_tmpfs_ok(account_factory, report_factory, report_data):
    tmp_fs = TempFS()
    data = report_data(2, 2)
    renderer = JSONRenderer(
        'runtime',
        tmp_fs.root_path,
        account_factory(),
        report_factory(),
    )
    output_file = renderer.render(data, f'{tmp_fs.root_path}/report')

    assert output_file == f'{tmp_fs.root_path}/report.json'
    assert open(output_file).read() == json.dumps(data)
