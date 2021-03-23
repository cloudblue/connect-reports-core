import os
import shutil
from functools import partial
import tempfile
import zipfile

from weasyprint import HTML, default_url_fetcher

from connect.reports.renderers.j2 import Jinja2Renderer
from connect.reports.renderers.registry import register


def local_fetcher(url, root_dir=None, template_dir=None):
    base_path = os.path.join(
        os.path.abspath(root_dir),
        template_dir,
    )
    if url.startswith('file://') and not url.startswith(f'file://{base_path}'):
        cwd = os.getcwd()
        rel_path = os.path.relpath(url[7:], cwd)
        new_path = os.path.join(
            os.path.abspath(root_dir),
            template_dir,
            rel_path,
        )
        new_url = f'file://{new_path}'
        return default_url_fetcher(new_url)
    return default_url_fetcher(url)


@register('pdf')
class PDFRenderer(Jinja2Renderer):
    def render(self, data, output_file):
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_filepath = super().render(data, output_file)
            with zipfile.ZipFile(zip_filepath) as zip_file:
                zip_file.extract(member='report.html', path=tmpdir)
                zip_file.extract(member='summary.json', path=tmpdir)

            os.remove(zip_filepath)
            shutil.move(
                f'{tmpdir}/report.html',
                f'{tmpdir}/report.tmp',
            )
            fetcher = partial(
                local_fetcher,
                root_dir=self.root_dir,
                template_dir=os.path.dirname(self.template),
            )

            html = HTML(filename=f'{tmpdir}/report.tmp', url_fetcher=fetcher)
            report_file = f'{tmpdir}/report.pdf'
            html.write_pdf(report_file)

            summary_file = f'{tmpdir}/summary.json'
            output_file = f'{output_file}.zip'
            with zipfile.ZipFile(output_file, 'w') as repfile:
                repfile.write(report_file, os.path.basename(report_file))
                repfile.write(summary_file, os.path.basename(summary_file))

        return output_file

    @classmethod
    def validate(cls, definition):
        errors = super(PDFRenderer, cls).validate(definition)
        if definition.args is not None:
            css_file = definition.args.get('css_file')
            if css_file and not os.path.isfile(
                os.path.join(definition.root_path, css_file),
            ):
                errors.append(
                    f'css_file `{css_file}` not found.',
                )
        return errors
