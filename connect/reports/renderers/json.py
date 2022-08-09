#  Copyright © 2022 CloudBlue. All rights reserved.

import inspect
import os

import orjson

from connect.reports.renderers.base import BaseRenderer
from connect.reports.renderers.registry import register


@register('json')
class JSONRenderer(BaseRenderer):
    """
    JSON Renderer class.
    Inherits from BaseRenderer class and implements
    the generation report function, exporting the data
    to a JSON file.
    """
    def generate_report(self, data, output_file):
        tokens = output_file.split('.')
        if tokens[-1] != 'json':
            output_file = f'{tokens[0]}.json'
        if inspect.isgenerator(data):
            has_data = False
            with open(output_file, 'wb') as f:
                f.write(b'[')
                for item in data:
                    has_data = True
                    f.write(orjson.dumps(item))
                    f.write(b',')
            if has_data:
                with open(output_file, 'rb+') as f:
                    f.seek(-1, os.SEEK_END)
                    f.truncate()
            with open(output_file, 'a') as f:
                f.write(']')
        else:
            with open(output_file, 'wb') as f:
                f.write(orjson.dumps(data))
        return output_file

    async def generate_report_async(self, data, output_file):
        tokens = output_file.split('.')
        if tokens[-1] != 'json':
            output_file = f'{tokens[0]}.json'
        if inspect.isasyncgen(data):
            has_data = False
            with open(output_file, 'wb') as f:
                await self._to_thread(f.write, b'[')
                async for item in data:
                    has_data = True
                    await self._to_thread(f.write, orjson.dumps(item))
                    await self._to_thread(f.write, b',')
            if has_data:
                with open(output_file, 'rb+') as f:
                    await self._to_thread(f.seek, -1, os.SEEK_END)
                    await self._to_thread(f.truncate)
            with open(output_file, 'a') as f:
                await self._to_thread(f.write, ']')
        else:
            with open(output_file, 'wb') as f:
                await self._to_thread(f.write, orjson.dumps(data))
        return output_file
