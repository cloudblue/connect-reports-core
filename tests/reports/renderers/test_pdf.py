#  Copyright © 2021 CloudBlue. All rights reserved.

import pytest

from fs.tempfs import TempFS

from connect.reports.datamodels import RendererDefinition
from connect.reports.renderers import PDFRenderer
from connect.reports.renderers.pdf import local_fetcher


@pytest.mark.parametrize('args', (None, {}, {'css_file': 'my/css_file.css'}))
def test_validate_ok(mocker, args):
    mocker.patch('connect.reports.renderers.pdf.os.path.isfile', return_value=True)

    defs = RendererDefinition(
        root_path='root_path',
        id='renderer_id',
        type='pdf',
        description='description',
        template='template.html.j2',
        args=args,
    )

    assert PDFRenderer.validate(defs) == []


def test_validate_css_not_found(mocker):
    mocker.patch('connect.reports.renderers.pdf.os.path.isfile', side_effect=[True, False])

    defs = RendererDefinition(
        root_path='root_path',
        id='renderer_id',
        type='pdf',
        description='description',
        template='template.html.j2',
        args={'css_file': 'my/css_file.css'},
    )

    assert PDFRenderer.validate(defs) == ['css_file `my/css_file.css` not found.']


@pytest.mark.parametrize(
    ('url', 'expected_url'),
    (
        ('https://example.com/image.png', 'https://example.com/image.png'),
        ('file://image.png', 'file:///root_dir/template_dir/image.png'),
        ('file:///root_dir/template_dir/image.png', 'file:///root_dir/template_dir/image.png'),
        ('file://images/image.png', 'file:///root_dir/template_dir/images/image.png'),
    ),
)
def test_local_fetcher(mocker, url, expected_url):
    def_fetcher = mocker.patch('connect.reports.renderers.pdf.default_url_fetcher')

    local_fetcher(url, root_dir='/root_dir', template_dir='template_dir')

    def_fetcher.assert_called_once_with(expected_url)


def test_render(mocker, account_factory, report_factory, report_data):
    mocker.patch('connect.reports.renderers.pdf.Jinja2Renderer.render', return_value='report.html')
    mocked_mv = mocker.patch('connect.reports.renderers.pdf.shutil.move')
    html = mocker.MagicMock()
    mocked_html = mocker.patch('connect.reports.renderers.pdf.HTML', return_value=html)
    fetcher = mocker.MagicMock()
    mocked_partial = mocker.patch('connect.reports.renderers.pdf.partial', return_value=fetcher)
    mocked_unlink = mocker.patch('connect.reports.renderers.pdf.os.unlink')

    renderer = PDFRenderer(
        'runtime environment', 'root_dir',
        account_factory(),
        report_factory(),
        template='report_dir/template.html.j2',
    )
    data = report_data()
    assert renderer.render(data, 'report') == 'report.pdf'

    mocked_mv.assert_called_once_with('report.html', 'report.temp')
    mocked_partial.assert_called_once_with(
        local_fetcher, root_dir='root_dir', template_dir='report_dir',
    )
    assert mocked_html.mock_calls[0].kwargs['filename'] == 'report.temp'
    assert mocked_html.mock_calls[0].kwargs['url_fetcher'] == fetcher

    html.write_pdf.assert_called_once_with('report.pdf')
    mocked_unlink.assert_called_once_with('report.temp')


def test_validate_tmpfs_template_wrong_name():
    tmp_fs = TempFS()
    tmp_fs.makedirs('package/report')
    tmp_fs.create('package/report/template.html.j3')
    tmp_fs.create('css_file.css')
    definition = RendererDefinition(
        root_path=tmp_fs.root_path,
        id='renderer_id',
        type='pdf',
        description='description',
        template='package/report/template.html.j3',
        args={'css_file': 'css_file.css'},
    )
    errors = PDFRenderer.validate(definition)

    assert f"invalid template name: `{definition.template}`" in errors[0]


def test_validate_tmpfs_css_missing():
    tmp_fs = TempFS()
    tmp_fs.makedirs('package/report')
    tmp_fs.create('package/report/template.html.j2')
    definition = RendererDefinition(
        root_path=tmp_fs.root_path,
        id='renderer_id',
        type='pdf',
        description='description',
        template='package/report/template.html.j2',
        args={'css_file': 'package/report/css_file.css'},
    )
    errors = PDFRenderer.validate(definition)

    assert f"css_file `{definition.args['css_file']}` not found." == errors[0]


def test_render_tmpfs_ok(report_data, account_factory, report_factory):
    tmp_fs = TempFS()
    tmp_fs.makedirs('package/report')
    with tmp_fs.open('package/report/template.html.j2', 'w') as fp:
        fp.write('''
            <html>
                <head><title>PDF Report</title></head>
                <body>
                    <ul>
                        {% for item in data %}
                        <li>{{item[0]}} {{item[1]}}</li>
                        {% endfor %}
                    </ul>
                </body>
            </html>
        ''')
    renderer = PDFRenderer(
        'runtime',
        tmp_fs.root_path,
        account_factory(),
        report_factory(),
        template='package/report/template.html.j2',
    )
    data = report_data(2, 2)
    path_to_output = f'{tmp_fs.root_path}/package/report/report'
    output_file = renderer.render(data, path_to_output)

    assert output_file == f'{path_to_output}.pdf'
    assert 'PDF Report' in str(open(output_file, 'rb').read())
