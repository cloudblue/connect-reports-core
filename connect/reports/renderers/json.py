#  Copyright © 2021 CloudBlue. All rights reserved.

import inspect

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
            sep = b''
            with open(output_file, 'wb') as f:
                f.write(b'[')
                for item in data:
                    f.write(sep)
                    f.write(orjson.dumps(item))
                    if sep == b'':
                        sep = b','
                f.write(b']')
        else:
            with open(output_file, 'wb') as f:
                f.write(orjson.dumps(data))
        return output_file
