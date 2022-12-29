#  Copyright © 2022 CloudBlue. All rights reserved.

from datetime import date, datetime, time
from zipfile import ZipFile

import orjson
import pytest
from fs.tempfs import TempFS

from connect.reports.datamodels import RendererDefinition
from connect.reports.renderers import JSONRenderer


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
            assert repfile.read().decode('utf-8') == orjson.dumps(data).decode('utf-8')


def test_generate_report_dict(account_factory, report_factory):
    tmp_fs = TempFS()
    data = {
        'key': 'value',
        'int': 3,
        'float': 3.4,
        'datetime': datetime.now(),
        'date': date.today(),
        'time': time(12, 11, 10),
    }
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
            assert repfile.read().decode('utf-8') == orjson.dumps(data).decode('utf-8')


def test_generate_report_generator(account_factory, report_factory):
    tmp_fs = TempFS()
    data = ({'key': 'value'} for _ in range(10))
    renderer = JSONRenderer(
        'runtime',
        tmp_fs.root_path,
        account_factory(),
        report_factory(),
    )
    output_file = renderer.render(data, f'{tmp_fs.root_path}/report')
    assert output_file == f'{tmp_fs.root_path}/report.zip'
    data = ({'key': 'value'} for _ in range(10))
    with ZipFile(output_file) as repzip:
        assert sorted(repzip.namelist()) == ['report.json', 'summary.json']
        with repzip.open('report.json') as repfile:
            assert repfile.read().decode('utf-8') == orjson.dumps(list(data)).decode('utf-8')


def test_generate_report_generator_no_data(account_factory, report_factory):
    tmp_fs = TempFS()

    def fakegen():
        if False:
            yield
    data = fakegen()
    renderer = JSONRenderer(
        'runtime',
        tmp_fs.root_path,
        account_factory(),
        report_factory(),
    )
    output_file = renderer.render(data, f'{tmp_fs.root_path}/report')
    assert output_file == f'{tmp_fs.root_path}/report.zip'
    data = ({'key': 'value'} for _ in range(10))
    with ZipFile(output_file) as repzip:
        assert sorted(repzip.namelist()) == ['report.json', 'summary.json']
        with repzip.open('report.json') as repfile:
            assert repfile.read().decode('utf-8') == orjson.dumps([]).decode('utf-8')


@pytest.mark.asyncio
async def test_render_async_with_list(account_factory, report_factory, report_data):
    tmp_fs = TempFS()
    data = report_data(2, 2)
    renderer = JSONRenderer(
        'runtime',
        tmp_fs.root_path,
        account_factory(),
        report_factory(),
    )
    output_file = await renderer.render_async(data, f'{tmp_fs.root_path}/report')

    assert output_file == f'{tmp_fs.root_path}/report.zip'
    with ZipFile(output_file) as repzip:
        assert sorted(repzip.namelist()) == ['report.json', 'summary.json']
        with repzip.open('report.json') as repfile:
            assert repfile.read().decode('utf-8') == orjson.dumps(data).decode('utf-8')


@pytest.mark.asyncio
async def test_render_async_with_async_generator(account_factory, report_factory, report_data_gen):
    tmp_fs = TempFS()
    data = [d for d in report_data_gen(2, 2)]

    async def async_gen(cols, rows):
        for d in report_data_gen(cols, rows):
            yield d

    renderer = JSONRenderer(
        'runtime',
        tmp_fs.root_path,
        account_factory(),
        report_factory(),
    )
    output_file = await renderer.render_async(async_gen(2, 2), f'{tmp_fs.root_path}/report')
    assert output_file == f'{tmp_fs.root_path}/report.zip'
    with ZipFile(output_file) as repzip:
        assert sorted(repzip.namelist()) == ['report.json', 'summary.json']
        with repzip.open('report.json') as repfile:
            assert repfile.read().decode('utf-8') == orjson.dumps(data).decode('utf-8')
