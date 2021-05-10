#  Copyright © 2021 CloudBlue. All rights reserved.

import inspect
import json
import os

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
            with open(output_file, 'w') as f:
                f.write('[')
                for item in data:
                    has_data = True
                    f.write(f'{json.dumps(item)}, ')
            if has_data:
                with open(output_file, 'rb+') as f:
                    f.seek(-2, os.SEEK_END)
                    f.truncate()
            with open(output_file, 'a') as f:
                f.write(']')
        else:
            json.dump(data, open(output_file, 'w'))
        return output_file
