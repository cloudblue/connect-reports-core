import os

from jinja2 import Environment, FileSystemLoader


from connect.reports.renderers.base import BaseRenderer
from connect.reports.renderers.registry import register


@register('jinja2')
class Jinja2Renderer(BaseRenderer):
    def render(self, data, output_file):
        path, name = self.template.rsplit('/', 1)
        loader = FileSystemLoader(os.path.join(self.root_dir, path))
        env = Environment(loader=loader)
        template = env.get_template(name)
        _, ext, _ = name.rsplit('.', 2)
        output_file = f'{output_file}.{ext}' if ext else output_file
        template.stream(self.get_context(data)).dump(open(output_file, 'w'))
        return output_file

    @classmethod
    def validate(cls, definition):
        errors = []
        if definition.template is None:
            errors.append('`template` is required for jinja2 renderer.')
        else:
            if not os.path.isfile(
                os.path.join(definition.root_path, definition.template),
            ):
                errors.append(f'template `{definition.template}` not found.')

            tokens = definition.template.rsplit('.', 2)
            if len(tokens) < 2 or tokens[-1] != 'j2':
                errors.append(
                    f'invalid template name: `{definition.template}` '
                    '(must be in the form <name>.<ext>.j2 or <name>.j2).',
                )

        return errors
