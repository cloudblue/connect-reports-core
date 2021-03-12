import os
import shutil
from functools import partial

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
        rendered_file = super().render(data, output_file)
        temp_file = f'{output_file}.temp'
        shutil.move(
            rendered_file,
            temp_file,
        )

        fetcher = partial(
            local_fetcher,
            root_dir=self.root_dir,
            template_dir=os.path.dirname(self.template),
        )

        html = HTML(filename=temp_file, url_fetcher=fetcher)
        output_file = f'{output_file}.pdf'
        html.write_pdf(output_file)
        os.unlink(temp_file)
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
