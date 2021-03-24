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


def test_generate_summary(account_factory, report_factory):
    tmp_fs = TempFS()
    account = account_factory()
    report = report_factory()
    renderer = JSONRenderer(
        'runtime',
        tmp_fs.root_path,
        account,
        report,
    )
    output_file = renderer.generate_summary(
        f'{tmp_fs.root_path}/summary',
        start_time=datetime.now(),
    )

    assert output_file == f'{tmp_fs.root_path}/summary.json'


def test_render(account_factory, report_factory, report_data):
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
