from connect.reports.renderers.base import BaseRenderer
from connect.reports.renderers.registry import register

from datetime import datetime
import tempfile
import zipfile
import os
import csv

import pytz


@register('csv')
class CSVRenderer(BaseRenderer):
    def render(self, data, output_file):
        start_time = datetime.now(tz=pytz.utc)

        with tempfile.TemporaryDirectory() as tmpdir:
            report_file = f'{tmpdir}/report.csv'
            with open(report_file, 'w') as fp:
                writer = csv.writer(fp, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
                for row in data:
                    writer.writerow(row)

            summary_file = self._add_info_csv(start_time, f'{tmpdir}/summary.csv')

            output_file = f'{output_file}.zip'
            with zipfile.ZipFile(output_file, 'w') as repzip:
                repzip.write(report_file, os.path.basename(report_file))
                repzip.write(summary_file, os.path.basename(summary_file))

        return output_file

    def _add_info_csv(self, start_time, output_file):
        values = []
        values.append(('', 'Report Execution Information'))
        values.append(('report_start_time', f'{start_time.isoformat()}'))
        values.append(('report_finish_time', f'{datetime.now(tz=pytz.utc).isoformat()}'))
        values.append(('account_id', f'{self.account.id}'))
        values.append(('account_name', f'{self.account.name}'))
        values.append(('report_id', f'{self.report.id}'))
        values.append(('report_name', f'{self.report.name}'))
        values.append(('runtime_environment', f'{self.environment}'))
        values.append(('report_execution_parameters', f'{self.report.values}'))

        with open(output_file, 'w') as fp:
            writer = csv.writer(fp, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            for value in values:
                writer.writerow(value)

        return output_file
