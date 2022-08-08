#  Copyright © 2022 CloudBlue. All rights reserved.

import os
from dataclasses import asdict, dataclass, field
from functools import cached_property
from typing import Any, Dict, List


@dataclass
class Account:
    id: str
    name: str


@dataclass
class Report:
    id: str
    name: str
    description: str
    values: List[Dict[str, Any]]


@dataclass
class RendererDefinition:
    """
    Renderer representation on `reports.json` file descriptor.

    :param root_path: Base root path.
    :type root_path: str
    :param id: Unique renderer identifier.
    :type id: str
    :param type: Renderer type.
    :type type: str
    :param description: Brief explanation about renderer.
    :type description: str
    :param default: Active/Inactive renderer.
    :type default: bool
    :param template: Template name
    :type template: str
    :param args: Additional arguments for using the renderer.
    :type args: dict
    """
    root_path: str
    id: str
    type: str
    description: str
    default: bool = False
    template: str = field(default=None)
    args: Dict[str, Any] = field(default=None)


@dataclass
class ParameterDefinition:
    """
    Parameter representation on `reports.json` file descriptor.

    :param id: Unique parameter identifier.
    :type id: str
    :param type: Parameter type.
    :type type: str
    :param name: Parameter name.
    :type name: str
    :param description: Brief explanation about parameter.
    :type description: str
    :param required: Required parameter.
    :type required: bool
    """
    id: str
    type: str
    name: str
    description: str
    required: bool = False


@dataclass
class ChoicesParameterDefinition(ParameterDefinition):
    choices: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class ReportDefinition:
    """
    Report representation on `reports.json` file descriptor.

    :param root_path: Base root path.
    :type root_path: str
    :param name: Report name.
    :type name: str
    :param readme_file: Brief explanation about report.
    :type readme_file: str
    :param entrypoint: Function responsible to generate the report.
    :type entrypoint: str
    :param audience: Report audience.
    :type audience: list
    :param report_spec: Report specification.
    :type report_spec: str
    :param renderers: List of available renderers for report.
    :type renderers: list
    :param parameters: List of report parameters.
    :type parameters: list
    """
    root_path: str
    name: str
    readme_file: str
    entrypoint: str
    audience: List[str]
    report_spec: str
    renderers: List[RendererDefinition]
    parameters: List[ParameterDefinition] = field(default_factory=list)

    @cached_property
    def default_renderer(self):
        for renderer in self.renderers:
            if renderer.default:
                return renderer.id

    @property
    def local_id(self):
        tokens = self.entrypoint.split('.')
        return tokens[1] if len(tokens) > 2 else None

    @property
    def description(self):
        path = os.path.join(self.root_path, self.readme_file)
        with open(path, 'r') as fp:
            return fp.read()

    def get_parameters(self):
        return [
            asdict(p)
            for p in self.parameters
        ]

    def get_renderers(self):
        renderer_list = []
        for renderer in self.renderers:
            renderer_list.append(
                {
                    'id': renderer.id,
                    'type': renderer.type,
                    'description': renderer.description,
                    'default': renderer.default,
                    'template': renderer.template,
                    'args': renderer.args,
                },
            )
        return renderer_list


@dataclass
class RepositoryDefinition:
    """
    Report repository representation on `reports.json` file descriptor.

    :param root_path: Base root path.
    :type root_path: str
    :param readme_file: Brief explanation about report repository.
    :type readme_file: str
    :param name: Repository name.
    :type name: str
    :param version: Repository version.
    :type version: str
    :param language: Supported language for report generation.
    :type language: str
    :param reports: List of available reports.
    :type reports: list
    """
    root_path: str
    readme_file: str
    name: str
    version: str
    language: str = 'python'
    reports: List[ReportDefinition] = field(default_factory=list)

    @property
    def description(self):
        path = os.path.join(self.root_path, self.readme_file)
        with open(path, 'r') as fp:
            return fp.read()
