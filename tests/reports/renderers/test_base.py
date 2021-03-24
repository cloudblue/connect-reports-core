#  Copyright © 2021 CloudBlue. All rights reserved.

import pytest

from fs.tempfs import TempFS

from zipfile import ZipFile

from connect.reports.renderers.base import BaseRenderer
from connect.reports.datamodels import RendererDefinition


def test_generate_report():
    with pytest.raises(NotImplementedError):
        BaseRenderer.generate_report(None, None, None)


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


def test_validate_ok():
    defs = RendererDefinition(
        root_path='root_path',
        id='renderer_id',
        type='json',
        description='description',
    )

    assert BaseRenderer.validate(defs) == []
