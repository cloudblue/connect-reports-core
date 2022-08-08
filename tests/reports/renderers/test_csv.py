#  Copyright © 2022 CloudBlue. All rights reserved.

from connect.reports.datamodels import RendererDefinition
from connect.reports.renderers.csv import CSVRenderer

import pytest

from fs.tempfs import TempFS

from zipfile import ZipFile


def test_validate_ok():

    defs = RendererDefinition(
        root_path='root_path',
        id='renderer_id',
        type='csv',
        description='description',
    )

    assert CSVRenderer.validate(defs) == []


def test_render(account_factory, report_factory):
    with TempFS() as tmp_fs:
        data = [['line1'], ['line2']]
        renderer = CSVRenderer(
            'runtime',
            tmp_fs.root_path,
            account_factory(),
            report_factory(),
        )
        output_file = renderer.render(data, f'{tmp_fs.root_path}/report')

        assert output_file == f'{tmp_fs.root_path}/report.zip'

        with ZipFile(output_file) as repzip:
            assert sorted(repzip.namelist()) == ['report.csv', 'summary.json']
            with repzip.open('report.csv') as repfile:
                content = repfile.read().decode('utf-8').split()
                assert content[0] == f'"{data[0][0]}"'
                assert content[1] == f'"{data[1][0]}"'


@pytest.mark.asyncio
async def test_render_async(account_factory, report_factory):
    async def async_generator():
        yield ['line1']
        yield ['line2']

    with TempFS() as tmp_fs:
        async_data = async_generator()
        data = [['line1'], ['line2']]
        renderer = CSVRenderer(
            'runtime',
            tmp_fs.root_path,
            account_factory(),
            report_factory(),
        )
        output_file = await renderer.render_async(async_data, f'{tmp_fs.root_path}/report')
        assert output_file == f'{tmp_fs.root_path}/report.zip'

        with ZipFile(output_file) as repzip:
            assert sorted(repzip.namelist()) == ['report.csv', 'summary.json']
            with repzip.open('report.csv') as repfile:
                content = repfile.read().decode('utf-8').split()
                assert content[0] == f'"{data[0][0]}"'
                assert content[1] == f'"{data[1][0]}"'


@pytest.mark.asyncio
async def test_render_async_generator_sync(account_factory, report_factory):
    with TempFS() as tmp_fs:
        data = [['line1'], ['line2']]
        renderer = CSVRenderer(
            'runtime',
            tmp_fs.root_path,
            account_factory(),
            report_factory(),
        )
        output_file = await renderer.render_async(data, f'{tmp_fs.root_path}/report')
        assert output_file == f'{tmp_fs.root_path}/report.zip'

        with ZipFile(output_file) as repzip:
            assert sorted(repzip.namelist()) == ['report.csv', 'summary.json']
            with repzip.open('report.csv') as repfile:
                content = repfile.read().decode('utf-8').split()
                assert content[0] == f'"{data[0][0]}"'
                assert content[1] == f'"{data[1][0]}"'
