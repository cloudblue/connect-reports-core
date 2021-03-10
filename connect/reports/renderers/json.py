import json

from connect.reports.renderers.base import BaseRenderer
from connect.reports.renderers.registry import register


@register('json')
class JSONRenderer(BaseRenderer):
    def render(self, data, output_file):
        output_file = f'{output_file}.json'
        json.dump(data, open(output_file, 'w'))
        return output_file
