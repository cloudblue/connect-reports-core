from connect.reports.datamodels import (
    ChoicesParameterDefinition,
    ParameterDefinition,
    RendererDefinition,
    ReportDefinition,
    RepositoryDefinition,
)


def parse(root_path, data):
    reports = data.pop('reports')
    reports_definitions = []
    for report in reports:
        parameters_definitions = []
        for param in report.pop('parameters'):
            cls = ChoicesParameterDefinition if 'choices' in param else ParameterDefinition
            parameters_definitions.append(cls(**param))

        if report['report_spec'] == '1':
            default_renderer = 'default_xlsx_renderer'
            template = report.pop('template')
            start_row = report.pop('start_row')
            start_col = report.pop('start_col')
            renderers_definitions = [
                RendererDefinition(
                    root_path=root_path,
                    id=default_renderer,
                    type='xlsx',
                    description='Render report to Excel.',
                    template=template,
                    args={
                        'start_row': start_row,
                        'start_col': start_col,
                    }),
            ]
        if report['report_spec'] == '2':
            default_renderer = report.pop('default_renderer')
            renderers_definitions = [
                RendererDefinition(root_path=root_path, **renderer)
                for renderer in report.pop('renderers')
            ]

        reports_definitions.append(
            ReportDefinition(
                root_path=root_path,
                default_renderer=default_renderer,
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
