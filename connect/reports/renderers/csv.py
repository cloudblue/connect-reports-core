#  Copyright © 2022 CloudBlue. All rights reserved.

import csv
import inspect

from connect.reports.renderers.base import BaseRenderer
from connect.reports.renderers.registry import register
from connect.reports.renderers.utils import aiter


@register('csv')
class CSVRenderer(BaseRenderer):
    """
    CSV Renderer class.
    Inherits from BaseRenderer class and implements
    the generation report function, exporting the data
    to a CSV file.
    """
    def generate_report(self, data, output_file):
        tokens = output_file.split('.')
        if tokens[-1] != 'csv':
            output_file = f'{tokens[0]}.csv'
        with open(output_file, 'w') as fp:
            writer = csv.writer(fp, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            for row in data:
                writer.writerow(row)
        return output_file

    async def generate_report_async(self, data, output_file):
        tokens = output_file.split('.')
        if tokens[-1] != 'csv':
            output_file = f'{tokens[0]}.csv'
        with open(output_file, 'w') as fp:
            writer = csv.writer(fp, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
            if not inspect.isasyncgen(data):
                data = aiter(data)
            async for row in data:
                await self._to_thread(writer.writerow, row)
        return output_file
