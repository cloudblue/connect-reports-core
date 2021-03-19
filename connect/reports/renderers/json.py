from connect.reports.renderers.base import BaseRenderer
from connect.reports.renderers.registry import register

from datetime import datetime
import json
import tempfile
import zipfile
import os

import pytz


@register('json')
class JSONRenderer(BaseRenderer):
    def render(self, data, output_file):
        start_time = datetime.now(tz=pytz.utc)

        with tempfile.TemporaryDirectory() as tmpdir:
            report_file = f'{tmpdir}/report.json'
            json.dump(data, open(report_file, 'w'))
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
