#  Copyright © 2022 CloudBlue. All rights reserved.

import asyncio
import contextlib
import json
import os
import shutil
import tempfile
import zipfile
from abc import ABCMeta, abstractmethod
from datetime import datetime
from functools import partial

import pytz


@contextlib.contextmanager
def temp_dir():
    name = tempfile.mkdtemp()
    yield name
    try:
        if os.path.isdir(name):
            shutil.rmtree(name)
    except Exception:
        pass


class BaseRenderer(metaclass=ABCMeta):
    """
    Base renderer class with minimum required functionality
    that renderers have to inherit and implement.

    :param environment: Runtime environment.
    :type environment: str
    :param root_dir: Base root dir.
    :type root_dir: str
    :param account: Owner account.
    :type account: Account
    :param report: Report object.
    :type report: Report
    :param template: Template name.
    :type template: str
    :param args: Renderer required arguments.
    :type args: dict
    :param extra_context: Additional context data
                        for report rendering.
    :type extra_context: dict
    """
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
        self.current_working_directory = None

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
        """
        Creates effectively report pack file (report + summary files)

        :param data: Report information.
        :type data: dict
        :param output_file: Output file name.
        :type output_file: str
        :param start_time: Start time information.
        :type start_time: datetime
        """
        start_time = start_time or datetime.now(tz=pytz.utc)
        with temp_dir() as tmpdir:
            self.current_working_directory = tmpdir
            report_file = self.generate_report(data, f'{tmpdir}/report')
            summary_file = self.generate_summary(f'{tmpdir}/summary', start_time)
            pack_file = self.pack_files(report_file, summary_file, output_file)
        return pack_file

    async def render_async(self, data, output_file, start_time=None):
        start_time = start_time or datetime.now(tz=pytz.utc)
        with temp_dir() as tmpdir:
            self.current_working_directory = tmpdir
            report_file = await self.generate_report_async(data, f'{tmpdir}/report')
            summary_file = await self.generate_summary_async(f'{tmpdir}/summary', start_time)
            pack_file = await self.pack_files_async(report_file, summary_file, output_file)
        return pack_file

    def generate_summary(self, output_file, start_time):
        """
        Generates summary information of report generation.

        :param output_file: Output file name.
        :type output_file: str
        :param start_time: Start time information.
        :type start_time: datetime
        """
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

    async def generate_summary_async(self, output_file, start_time):
        return await self._to_thread(self.generate_summary, output_file, start_time)

    def pack_files(self, report_file, summary_file, output_file):
        tokens = output_file.split('.')
        if tokens[-1] != 'zip':
            output_file = f'{tokens[0]}.zip'
        with zipfile.ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED) as repzip:
            repzip.write(report_file, os.path.basename(report_file))
            repzip.write(summary_file, os.path.basename(summary_file))
        return output_file

    async def pack_files_async(self, report_file, summary_file, output_file):
        return await self._to_thread(self.pack_files, report_file, summary_file, output_file)

    async def _to_thread(self, func, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(func, **kwargs), *args)

    @abstractmethod
    def generate_report(self, data, output_file):
        """
        Method to be implemented by the specific renderer.
        Generates report file.

        :param data: Report information.
        :type data: dict
        :param output_file: Output file name.
        :type output_file: str
        """
        raise NotImplementedError('Subclasses must implement the `generate_report` method.')

    @abstractmethod
    async def generate_report_async(self, data, output_file):
        """
        Method to be implemented by the specific renderer.
        Generates report file.

        :param data: Report information.
        :type data: dict
        :param output_file: Output file name.
        :type output_file: str
        """
        raise NotImplementedError('Subclasses must implement the `generate_report_async` method.')

    @classmethod
    def validate(cls, definition):
        return []
