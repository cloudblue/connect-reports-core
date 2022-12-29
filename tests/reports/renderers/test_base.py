#  Copyright © 2022 CloudBlue. All rights reserved.
from zipfile import ZipFile

import pytest
from fs.tempfs import TempFS

from connect.reports.datamodels import RendererDefinition
from connect.reports.renderers.base import BaseRenderer, temp_dir


def test_generate_report():
    with pytest.raises(NotImplementedError):
        BaseRenderer.generate_report(None, None, None)


@pytest.mark.asyncio
async def test_generate_report_async():
    with pytest.raises(NotImplementedError):
        await BaseRenderer.generate_report_async(None, None, None)


@pytest.mark.parametrize(
    ('extra_context'),
    (
        {'name': 'test', 'desc': 'description'},
        None,
    ),
)
def test_render(account_factory, report_factory, report_data, extra_context):

    class DummyRenderer(BaseRenderer):

        def generate_report(self, data, output_file):
            output_file = f'{output_file}.ext'
            open(output_file, 'w').write(str(data))
            return output_file

        async def generate_report_async(self, data, output_file):
            pass

    tmp_fs = TempFS()
    data = report_data(2, 2)
    renderer = DummyRenderer(
        'runtime',
        tmp_fs.root_path,
        account_factory(),
        report_factory(),
    )
    renderer.set_extra_context(extra_context)
    ctx = renderer.get_context(data)

    output_file = renderer.render(data, f'{tmp_fs.root_path}/report')

    assert output_file == f'{tmp_fs.root_path}/report.zip'
    with ZipFile(output_file) as repzip:
        assert sorted(repzip.namelist()) == ['report.ext', 'summary.json']
        with repzip.open('report.ext') as repfile:
            assert repfile.read().decode('utf-8') == str(data)

    if extra_context:
        assert 'name' in ctx['extra_context']
        assert 'desc' in ctx['extra_context']


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('extra_context'),
    (
        {'name': 'test', 'desc': 'description'},
        None,
    ),
)
async def test_render_async(account_factory, report_factory, report_data, extra_context):

    class DummyRenderer(BaseRenderer):

        def generate_report(self, data, output_file):
            pass

        async def generate_report_async(self, data, output_file):
            output_file = f'{output_file}.ext'
            with open(output_file, 'w') as f:
                await self._to_thread(f.write, str(data))
            return output_file

    tmp_fs = TempFS()
    data = report_data(2, 2)
    renderer = DummyRenderer(
        'runtime',
        tmp_fs.root_path,
        account_factory(),
        report_factory(),
    )
    renderer.set_extra_context(extra_context)
    ctx = renderer.get_context(data)

    output_file = await renderer.render_async(data, f'{tmp_fs.root_path}/report')

    assert output_file == f'{tmp_fs.root_path}/report.zip'
    with ZipFile(output_file) as repzip:
        assert sorted(repzip.namelist()) == ['report.ext', 'summary.json']
        with repzip.open('report.ext') as repfile:
            assert repfile.read().decode('utf-8') == str(data)

    if extra_context:
        assert 'name' in ctx['extra_context']
        assert 'desc' in ctx['extra_context']


def test_validate_ok():
    defs = RendererDefinition(
        root_path='root_path',
        id='renderer_id',
        type='json',
        description='description',
    )

    assert BaseRenderer.validate(defs) == []


def test_temp_dir_windows(mocker):
    mocker.patch('connect.reports.renderers.base.tempfile.mkdtemp', return_value='folder')
    mocker.patch('connect.reports.renderers.base.os.path.isdir', side_effect=Exception)
    try:
        with temp_dir():
            pass
    except Exception as exc:
        raise AssertionError(f"'temp_dir' raised an exception {exc}")
