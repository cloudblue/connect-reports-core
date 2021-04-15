#  Copyright © 2021 CloudBlue. All rights reserved.

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
    root_path: str
    id: str
    type: str
    description: str
    default: bool = False
    template: str = field(default=None)
    args: Dict[str, Any] = field(default=None)


@dataclass
class ParameterDefinition:
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
        return [
            asdict(renderer)
            for renderer in self.renderers
        ]


@dataclass
class RepositoryDefinition:
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
