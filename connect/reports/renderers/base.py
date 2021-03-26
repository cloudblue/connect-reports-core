#  Copyright © 2021 CloudBlue. All rights reserved.

from abc import ABCMeta, abstractmethod
import zipfile
import os
from datetime import datetime
import tempfile
import json

import pytz


class BaseRenderer(metaclass=ABCMeta):
    def __init__(
        self,
        environment,
        root_dir,
        account,
        report,
        template=None,
        args=None,
    ):
        self.environment = environment
        self.root_dir = root_dir
        self.account = account
        self.report = report
        self.template = template
        self.args = args or {}
        self.extra_context = None

    def get_context(self, data):
        context = {
            'account': self.account,
            'report': self.report,
            'data': data,
        }
        if self.extra_context:
            context['extra_context'] = self.extra_context
        return context

    def set_extra_context(self, data):
        self.extra_context = data

    def render(self, data, output_file, start_time=None):
        start_time = start_time or datetime.now(tz=pytz.utc)
        with tempfile.TemporaryDirectory() as tmpdir:
            report_file = self.generate_report(data, f'{tmpdir}/report')
            summary_file = self.generate_summary(f'{tmpdir}/summary', start_time)
            pack_file = self.pack_files(report_file, summary_file, output_file)
        return pack_file

    def generate_summary(self, output_file, start_time):
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
                'report_execution_parameters': self.report.values,
            },
        }
        output_file = f'{output_file}.json'
        json.dump(data, open(output_file, 'w'), indent=4, sort_keys=True)
        return output_file

    def pack_files(self, report_file, summary_file, output_file):
        tokens = output_file.split('.')
        if tokens[-1] != 'zip':
            output_file = f'{tokens[0]}.zip'
        with zipfile.ZipFile(output_file, 'w') as repzip:
            repzip.write(report_file, os.path.basename(report_file))
            repzip.write(summary_file, os.path.basename(summary_file))

        return output_file

    @abstractmethod
    def generate_report(self, data, output_file):
        raise NotImplementedError('Subclasses must implement the `generate_report` method.')

    @classmethod
    def validate(cls, definition):
        return []
