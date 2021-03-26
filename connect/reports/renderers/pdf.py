#  Copyright © 2021 CloudBlue. All rights reserved.

import os
import tempfile
from datetime import datetime
from functools import partial

import pytz

from weasyprint import CSS, HTML, default_url_fetcher

from connect.reports.renderers.j2 import Jinja2Renderer
from connect.reports.renderers.registry import register


def local_fetcher(url, root_dir=None, template_dir=None, cwd=None):
    if url.startswith(f'file://{cwd}'):
        rel_path = os.path.relpath(url[7:], cwd)
        new_path = os.path.join(
            os.path.abspath(root_dir),
            rel_path,
        )
        url = f'file://{new_path}'
    elif url.startswith(f'file://{os.path.abspath(os.path.join(root_dir, template_dir))}'):
        count = url.count(template_dir)
        if url.count(template_dir) > 1:
            url = url.replace(f'{template_dir}/', '', count - 1)
    return default_url_fetcher(url)


@register('pdf')
class PDFRenderer(Jinja2Renderer):
    def render(self, data, output_file, start_time=None):
        start_time = start_time or datetime.now(tz=pytz.utc)
        with tempfile.TemporaryDirectory() as tmpdir:
            self.cwd = tmpdir
            report_file = self.generate_report(data, f'{tmpdir}/report')
            summary_file = self.generate_summary(f'{tmpdir}/summary', start_time)
            pack_file = self.pack_files(report_file, summary_file, output_file)
        return pack_file

    def generate_report(self, data, output_file):
        tokens = output_file.split('.')
        if tokens[-1] != 'pdf':
            output_file = f'{tokens[0]}.pdf'

        rendered_file = super().generate_report(data, output_file)
        fetcher = partial(
            local_fetcher,
            root_dir=self.root_dir,
            template_dir=os.path.dirname(self.template),
            cwd=getattr(self, 'cwd', os.getcwd()),
        )
        kwargs = {}
        css_file = self.args.get('css_file')
        if css_file:
            css = CSS(filename=os.path.join(self.root_dir, css_file), url_fetcher=fetcher)
            kwargs['stylesheets'] = [css]
        html = HTML(filename=rendered_file, url_fetcher=fetcher)
        html.write_pdf(output_file, **kwargs)
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
