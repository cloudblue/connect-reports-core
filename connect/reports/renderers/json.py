#  Copyright © 2021 CloudBlue. All rights reserved.

from connect.reports.renderers.base import BaseRenderer
from connect.reports.renderers.registry import register

import json


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
        json.dump(data, open(output_file, 'w'))
        return output_file
