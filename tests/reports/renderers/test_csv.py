from connect.reports.datamodels import RendererDefinition
from connect.reports.renderers.csv import CSVRenderer

from fs.tempfs import TempFS


def test_validate_ok():

    defs = RendererDefinition(
        root_path='root_path',
        id='renderer_id',
        type='csv',
        description='description',
    )

    assert CSVRenderer.validate(defs) == []


def test_render(account_factory, report_factory, report_data):
    data = [['linea1'], ['linea2']]
    test_filesystem = TempFS()
    filename = f'{test_filesystem.root_path}/report'
    renderer = CSVRenderer(
        'runtime environment',
        'root_dir',
        account_factory(),
        report_factory(),
    )
    csv_filename = renderer.render(data, filename)
    with open(csv_filename, 'r') as fp:
        content = fp.readlines()

    assert content[0] == f'"{data[0][0]}"\n'
    assert content[1] == f'"{data[1][0]}"\n'
    assert csv_filename == f'{filename}.csv'
