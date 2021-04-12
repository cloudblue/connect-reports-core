#  Copyright © 2021 CloudBlue. All rights reserved.

from connect.reports.datamodels import (
    ChoicesParameterDefinition,
    ParameterDefinition,
    RendererDefinition,
    ReportDefinition,
    RepositoryDefinition,
)
from connect.reports.constants import DEFAULT_RENDERER_ID


def parse(root_path, data):
    reports = data.pop('reports')
    reports_definitions = []
    for report in reports:
        parameters_definitions = []
        for param in report.pop('parameters'):
            cls = ChoicesParameterDefinition if 'choices' in param else ParameterDefinition
            parameters_definitions.append(cls(**param))

        if report['report_spec'] == '1':
            default_renderer = DEFAULT_RENDERER_ID
            template = report.pop('template')
            start_row = report.pop('start_row')
            start_col = report.pop('start_col')
            renderers_definitions = [
                RendererDefinition(
                    root_path=root_path,
                    id=default_renderer,
                    type='xlsx',
                    description='Render report to Excel.',
                    default=True,
                    template=template,
                    args={
                        'start_row': start_row,
                        'start_col': start_col,
                    }),
            ]
        if report['report_spec'] == '2':
            renderers_definitions = [
                RendererDefinition(root_path=root_path, **renderer)
                for renderer in report.pop('renderers')
            ]

        reports_definitions.append(
            ReportDefinition(
                root_path=root_path,
                parameters=parameters_definitions,
                renderers=renderers_definitions,
                **report,
            ),
        )

    return RepositoryDefinition(
        root_path=root_path,
        reports=reports_definitions,
        **data,
    )
