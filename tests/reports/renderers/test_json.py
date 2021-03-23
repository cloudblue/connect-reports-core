#  Copyright © 2021 CloudBlue. All rights reserved.

from connect.reports.datamodels import RendererDefinition
from connect.reports.renderers import JSONRenderer

from fs.tempfs import TempFS

from datetime import datetime
from zipfile import ZipFile
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
    mocked_dump = mocker.patch('connect.reports.renderers.json.json.dump')
    mocked_tmpdir = mocker.patch('connect.reports.renderers.json.tempfile.TemporaryDirectory')
    mocked_zipfile = mocker.patch('connect.reports.renderers.json.zipfile.ZipFile')

    data = report_data()
    renderer = JSONRenderer(
        'runtime environment',
        'root_dir',
        account_factory(),
        report_factory(),
    )
    output_file = renderer.render(data, 'report')

    assert output_file == 'report.zip'
    assert mocked_dump.mock_calls[0].args[0] == data
    assert mocked_open.mock_calls[0].args[0].rsplit('/', 1)[1] == 'report.json'
    assert mocked_open.mock_calls[0].args[1] == 'w'
    assert mocked_zipfile.call_count == 1
    assert mocked_tmpdir.call_count == 1


def test_add_info_json(account_factory, report_factory):
    tmp_fs = TempFS()

    values = [{'param_id': 'param_value'}]
    report = report_factory(values=values)
    start_time = datetime.utcnow()

    renderer = JSONRenderer(
        'runtime',
        tmp_fs.root_path,
        account_factory(),
        report,
    )
    output_file = renderer._add_info_json(start_time, f'{tmp_fs.root_path}/summary.json')
    data = json.load(open(output_file, 'r'))

    assert output_file == f'{tmp_fs.root_path}/summary.json'
    assert data['data']['report_start_time'] == start_time.isoformat()


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

    assert output_file == f'{tmp_fs.root_path}/report.zip'
    with ZipFile(output_file) as repzip:
        assert sorted(repzip.namelist()) == ['report.json', 'summary.json']
        with repzip.open('report.json') as repfile:
            assert repfile.read().decode('utf-8') == json.dumps(data)
