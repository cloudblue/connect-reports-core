#  Copyright © 2022 CloudBlue. All rights reserved.

import os
import pathlib

from weasyprint import CSS, HTML
from weasyprint.urls import URLFetcher

from connect.reports.renderers.j2 import Jinja2Renderer
from connect.reports.renderers.registry import register


class LocalURLFetcher(URLFetcher):
    """
    URL fetcher that maps the file URLs generated while rendering
    (relative to the temporary working directory) to the report root directory.
    """

    def __init__(self, root_dir=None, template_dir=None, cwd=None, **kwargs):
        super().__init__(**kwargs)
        self.root_dir = root_dir
        self.template_dir = template_dir
        self.cwd = cwd

    def fetch(self, url, headers=None):
        root_dir, template_dir, cwd = self.root_dir, self.template_dir, self.cwd
        tpl_dir_path = pathlib.Path(os.path.abspath(root_dir)) / pathlib.Path(template_dir)
        tpl_dir_url = tpl_dir_path.as_uri()
        if url.startswith(f'file://{cwd}'):
            rel_path = os.path.relpath(url[7:], cwd)
            new_path = os.path.join(
                os.path.abspath(root_dir),
                rel_path,
            )
            url = f'file://{new_path}'
        elif url.startswith(tpl_dir_url):
            count = url.count(template_dir)
            if url.count(template_dir) > 1:
                url = url.replace(f'{template_dir}/', '', count - 1)
        return super().fetch(url, headers)


@register('pdf')
class PDFRenderer(Jinja2Renderer):
    """
    PDF Renderer class.
    Inherits from BaseRenderer class and implements
    the generation report function, exporting the data
    to a PDF file.
    """

    def generate_report(self, data, output_file):
        tokens = output_file.split('.')
        if tokens[-1] != 'pdf':
            output_file = f'{tokens[0]}.pdf'

        rendered_file = super().generate_report(data, output_file)
        fetcher = LocalURLFetcher(
            root_dir=self.root_dir,
            template_dir=os.path.dirname(self.template),
            cwd=self.current_working_directory,
        )
        options = {'uncompressed_pdf': True}
        css_file = self.args.get('css_file')
        if css_file:
            css = CSS(filename=os.path.join(self.root_dir, css_file), url_fetcher=fetcher)
            options.update({'stylesheets': [css]})
        html = HTML(filename=rendered_file, url_fetcher=fetcher)
        html.write_pdf(output_file, **options)
        return output_file

    async def generate_report_async(self, data, output_file):
        tokens = output_file.split('.')
        if tokens[-1] != 'pdf':
            output_file = f'{tokens[0]}.pdf'

        rendered_file = await super().generate_report_async(data, output_file)
        fetcher = LocalURLFetcher(
            root_dir=self.root_dir,
            template_dir=os.path.dirname(self.template),
            cwd=self.current_working_directory,
        )

        def _generate():
            options = {'uncompressed_pdf': True}
            css_file = self.args.get('css_file')
            if css_file:
                css = CSS(filename=os.path.join(self.root_dir, css_file), url_fetcher=fetcher)
                options.update({'stylesheets': [css]})
            html = HTML(filename=rendered_file, url_fetcher=fetcher)
            html.write_pdf(output_file, **options)
        await self._to_thread(_generate)
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
