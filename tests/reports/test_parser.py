#  Copyright © 2022 CloudBlue. All rights reserved.

from connect.reports.parser import parse
from connect.reports.datamodels import (
    ParameterDefinition,
    RendererDefinition,
    ReportDefinition,
    RepositoryDefinition,
)


def test_parse_default(repo_json):
    repo = repo_json()
    defs = parse('fake_path', repo)

    assert isinstance(defs, RepositoryDefinition)
    assert len(defs.reports) == 2
    for report_def in defs.reports:
        assert isinstance(report_def, ReportDefinition)
        assert len(report_def.renderers) == 1
        assert isinstance(report_def.renderers[0], RendererDefinition)
        assert len(report_def.parameters) == 1
        assert isinstance(report_def.parameters[0], ParameterDefinition)
