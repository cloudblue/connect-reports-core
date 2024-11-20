#  Copyright © 2022 CloudBlue. All rights reserved.
from zipfile import ZipFile

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
        ('file:///root_dir/template_dir/image.png', 'file:///root_dir/template_dir/image.png'),
        (
            'file:///tmp/my_temp_dir/template_dir/image.png',
            'file:///root_dir/template_dir/image.png',
        ),
        (
            'file:///root_dir/template_dir/template_dir/image.png',
            'file:///root_dir/template_dir/image.png',
        ),
    ),
)
def test_local_fetcher(mocker, url, expected_url):
    def_fetcher = mocker.patch('connect.reports.renderers.pdf.default_url_fetcher')

    local_fetcher(url, root_dir='/root_dir', template_dir='template_dir', cwd='/tmp/my_temp_dir')

    def_fetcher.assert_called_once_with(expected_url)


def test_local_fetcher_root_with_spaces(mocker):
    url = 'file:///root%20dir/template_dir/template_dir/image.png'
    expected_url = 'file:///root%20dir/template_dir/image.png'
    def_fetcher = mocker.patch('connect.reports.renderers.pdf.default_url_fetcher')

    local_fetcher(url, root_dir='/root dir', template_dir='template_dir', cwd='/tmp/my_temp_dir')

    def_fetcher.assert_called_once_with(expected_url)


def test_generate_report(mocker, account_factory, report_factory, report_data):
    mocker.patch(
        'connect.reports.renderers.pdf.Jinja2Renderer.generate_report',
        return_value='report.pdf.html',
    )
    html = mocker.MagicMock()
    mocked_html = mocker.patch('connect.reports.renderers.pdf.HTML', return_value=html)
    fetcher = mocker.MagicMock()
    mocked_partial = mocker.patch('connect.reports.renderers.pdf.partial', return_value=fetcher)

    renderer = PDFRenderer(
        'runtime environment', 'root_dir',
        account_factory(),
        report_factory(),
        template='report_dir/template.html.j2',
    )
    data = report_data()
    assert renderer.generate_report(data, 'report.pdf') == 'report.pdf'

    mocked_partial.assert_called_once_with(
        local_fetcher, root_dir='root_dir', template_dir='report_dir', cwd=None,
    )
    assert mocked_html.mock_calls[0].kwargs['filename'] == 'report.pdf.html'
    assert mocked_html.mock_calls[0].kwargs['url_fetcher'] == fetcher

    html.write_pdf.assert_called_once_with('report.pdf', uncompressed_pdf=True)


def test_generate_report_external_css(mocker, account_factory, report_factory, report_data):
    mocker.patch(
        'connect.reports.renderers.pdf.Jinja2Renderer.generate_report',
        return_value='report.pdf.html',
    )
    html = mocker.MagicMock()
    mocked_html = mocker.patch('connect.reports.renderers.pdf.HTML', return_value=html)
    css = mocker.MagicMock()
    mocked_css = mocker.patch('connect.reports.renderers.pdf.CSS', return_value=css)
    fetcher = mocker.MagicMock()
    mocked_partial = mocker.patch('connect.reports.renderers.pdf.partial', return_value=fetcher)

    renderer = PDFRenderer(
        'runtime environment', 'root_dir',
        account_factory(),
        report_factory(),
        template='report_dir/template.html.j2',
        args={'css_file': 'report_dir/template.css'},
    )
    data = report_data()
    assert renderer.generate_report(data, 'report.pdf') == 'report.pdf'

    mocked_partial.assert_called_once_with(
        local_fetcher, root_dir='root_dir', template_dir='report_dir', cwd=None,
    )
    assert mocked_html.mock_calls[0].kwargs['filename'] == 'report.pdf.html'
    assert mocked_html.mock_calls[0].kwargs['url_fetcher'] == fetcher

    assert mocked_css.mock_calls[0].kwargs['filename'] == 'root_dir/report_dir/template.css'
    assert mocked_css.mock_calls[0].kwargs['url_fetcher'] == fetcher

    html.write_pdf.assert_called_once_with('report.pdf', uncompressed_pdf=True, stylesheets=[css])


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

    assert output_file == f'{path_to_output}.zip'
    with ZipFile(output_file) as zip_file:
        assert sorted(zip_file.namelist()) == ['report.pdf', 'summary.json']
        with zip_file.open('report.pdf', 'r') as fp:
            assert 'PDF Report' in str(fp.read())


@pytest.mark.asyncio
async def test_render_async_tmpfs_ok(report_data, account_factory, report_factory):
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
    with tmp_fs.open('package/report/template.css', 'w') as fp:
        fp.write('')
    renderer = PDFRenderer(
        'runtime',
        tmp_fs.root_path,
        account_factory(),
        report_factory(),
        template='package/report/template.html.j2',
        args={'css_file': 'package/report/template.css'},
    )
    data = report_data(2, 2)
    path_to_output = f'{tmp_fs.root_path}/package/report/report'
    output_file = await renderer.render_async(data, path_to_output)

    assert output_file == f'{path_to_output}.zip'
    with ZipFile(output_file) as zip_file:
        assert sorted(zip_file.namelist()) == ['report.pdf', 'summary.json']
        with zip_file.open('report.pdf', 'r') as fp:
            assert 'PDF Report' in str(fp.read())
