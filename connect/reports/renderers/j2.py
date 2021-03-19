import os
import json
from datetime import datetime
import tempfile
import zipfile

import pytz

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

        start_time = datetime.now(tz=pytz.utc)
        with tempfile.TemporaryDirectory() as tmpdir:
            report_file = f'{tmpdir}/report.{ext}'
            template.stream(self.get_context(data)).dump(open(report_file, 'w'))

            summary_file = self._add_info_json(start_time, f'{tmpdir}/summary.json')

            output_file = f'{output_file}.zip'
            with zipfile.ZipFile(output_file, 'w') as repzip:
                repzip.write(report_file, os.path.basename(report_file))
                repzip.write(summary_file, os.path.basename(summary_file))

        return output_file

    def _add_info_json(self, start_time, output_file):
        data = {
            'title': 'Report Execution Information',
            'data': {
                'report_start_time': start_time.isoformat(),
                'report_finish_time': datetime.now(tz=pytz.utc).isoformat(),
                'account_id': self.account.id,
                'account_name': self.account.name,
                'report_id': self.report.id,
                'report_name': self.report.name,
                'runtime_environment': self.environment,
                'report_execution_parameters': json.dumps(
                    self.report.values,
                    indent=4,
                    sort_keys=True,
                ),
            },
        }
        json.dump(data, open(output_file, 'w'))
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
            if len(tokens) < 3 or tokens[-1] != 'j2':
                errors.append(
                    f'invalid template name: `{definition.template}` '
                    '(must be in the form <name>.<ext>.j2).',
                )

        return errors
