import json
from datetime import datetime

import pytest

from fs.tempfs import TempFS

from openpyxl import Workbook

from connect.reports.datamodels import RendererDefinition
from connect.reports.renderers import XLSXRenderer


@pytest.mark.parametrize('args', (None, {}, {'start_row': 1, 'start_col': 1}))
def test_validate_ok(mocker, args):
    tmp_fs = TempFS()
    defs = RendererDefinition(
        root_path=tmp_fs.root_path,
        id='renderer_id',
        type='xlsx',
        description='description',
        template='template.xlsx',
        args=args,
    )
    _create_xlsx_doc(f'{tmp_fs.root_path}/{defs.template}')

    assert XLSXRenderer.validate(defs) == []


def test_validate_no_template():
    defs = RendererDefinition(
        root_path='root_path',
        id='renderer_id',
        type='xlsx',
        description='description',
    )

    assert XLSXRenderer.validate(defs) == ['`template` is required for xlsx renderer.']


def test_validate_template_not_found(mocker):
    mocker.patch('connect.reports.renderers.xlsx.os.path.isfile', return_value=False)
    defs = RendererDefinition(
        root_path='root_path',
        id='renderer_id',
        type='xlsx',
        description='description',
        template='template.xlsx',
    )

    assert XLSXRenderer.validate(defs) == ['template `template.xlsx` not found.']


@pytest.mark.parametrize(
    ('args', 'error'),
    (
        ({'start_row': 'a'}, '`start_row` must be integer.'),
        ({'start_col': 'a'}, '`start_col` must be integer.'),
        ({'start_row': 0}, '`start_row` must be greater than 0.'),
        ({'start_row': -3}, '`start_row` must be greater than 0.'),
        ({'start_col': 0}, '`start_col` must be greater than 0.'),
        ({'start_col': -3}, '`start_col` must be greater than 0.'),
    ),
)
def test_validate_invalid_args(mocker, args, error):
    tmp_fs = TempFS()
    defs = RendererDefinition(
        root_path=tmp_fs.root_path,
        id='renderer_id',
        type='xlsx',
        description='description',
        template='template.xlsx',
        args=args,
    )
    _create_xlsx_doc(f'{tmp_fs.root_path}/{defs.template}')

    assert XLSXRenderer.validate(defs) == [error]


def test_render(mocker, account_factory, report_factory, report_data):
    data = report_data()

    expected_calls = []
    for i in range(10):
        for j in range(10):
            expected_calls.append(mocker.call(2 + i, 1 + j, value=f'row_{i}_col_{j}'))

    data_sheet = mocker.MagicMock()
    info_sheet = mocker.MagicMock()

    wbmock = mocker.MagicMock()
    wbmock.__getitem__.side_effect = [data_sheet]
    wbmock.create_sheet.side_effect = [info_sheet]

    mocked_load_wb = mocker.patch(
        'connect.reports.renderers.xlsx.load_workbook',
        return_value=wbmock,
    )
    acc = account_factory()
    report = report_factory()

    renderer = XLSXRenderer(
        'runtime environment', 'root_path', acc, report, template='template.xlsx',
    )

    renderer._add_info_sheet = mocker.MagicMock()

    assert renderer.render(data, 'report') == 'report.xlsx'

    mocked_load_wb.assert_called_once_with('root_path/template.xlsx')

    data_sheet.cell.assert_has_calls(expected_calls)
    wbmock.create_sheet.assert_called_once_with('Info')
    wbmock.save.assert_called_once_with('report.xlsx')
    assert renderer._add_info_sheet.mock_calls[0].args[0] == info_sheet


def test_add_info_sheet(mocker, account_factory, report_factory):
    acc = account_factory()
    values = [{'param_id': 'param_value'}]
    report = report_factory(values=values)
    start_time = datetime.utcnow()

    renderer = XLSXRenderer(
        'runtime environment', 'root_path', acc, report, template='template.xlsx',
    )
    mocked_cells = {}

    def get_item(k):
        return mocked_cells.setdefault(k, mocker.MagicMock())

    ws = mocker.MagicMock()
    ws.__getitem__.side_effect = get_item

    renderer._add_info_sheet(ws, start_time)

    assert mocked_cells['B2'].value == start_time.isoformat()
    assert mocked_cells['B4'].value == acc.id
    assert mocked_cells['B5'].value == acc.name
    assert mocked_cells['B6'].value == report.id
    assert mocked_cells['B7'].value == report.name
    assert mocked_cells['B8'].value == 'runtime environment'
    assert json.loads(mocked_cells['B9'].value) == values


def test_validate_template_not_valid():

    tmp_filesystem = TempFS()
    tmp_filesystem.create('test.xlsx')

    defs = RendererDefinition(
        root_path=tmp_filesystem.root_path,
        id='renderer_id',
        type='xlsx',
        description='description',
        template='test.xlsx',
    )

    errors = XLSXRenderer.validate(defs)

    assert 'not valid or empty' in errors[0]


def _create_xlsx_doc(xlsx_path):
    wb = Workbook()
    ws = wb.active
    ws.title = "test"
    for _ in range(1, 10):
        ws.append(range(10))
    wb.save(xlsx_path)
