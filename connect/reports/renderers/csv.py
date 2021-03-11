from connect.reports.renderers.base import BaseRenderer
from connect.reports.renderers.registry import register


@register('csv')
class CSVRenderer(BaseRenderer):
    def render(self, data, output_file):
        output_file = f'{output_file}.csv'
        with open(output_file, 'w') as fp:
            for row in data:
                line = ','.join(f'"{str(item)}"' for item in row)
                fp.write(f'{line}\n')

        return output_file
