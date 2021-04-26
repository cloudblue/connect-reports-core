#  Copyright © 2021 CloudBlue. All rights reserved.

import json
import os
from collections import Counter

import jsonschema

from connect.reports.renderers import get_renderer_class, get_renderers


CHOICES_PARAM_TYPE = [
    'checkbox',
    'choice',
]

ALL_PARAM_TYPES = [
    'date_range',
    'date',
    'single_line',
    'object',
    'product',
    'marketplace',
    'hub',
    *CHOICES_PARAM_TYPE,
]

JSON_REPORTS_SCHEMA = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'schemas/reports_schema.json',
)


def _get_duplicates(data):
    return [
        item for item, count in Counter(data).items() if count > 1
    ]


def validate_with_schema(json_data):
    with open(JSON_REPORTS_SCHEMA, 'r') as fp:
        json_schema = json.load(fp)
    try:
        jsonschema.validate(instance=json_data, schema=json_schema)
    except jsonschema.exceptions.ValidationError as errors:
        return str(errors)


def _validate_parameters(report_id, parameters):
    errors = []
    params_ids = []
    for param in parameters:
        params_ids.append(param.id)

        if param.type not in ALL_PARAM_TYPES:
            errors.append(
                f'Invalid type for parameter `{param.id}` on report `{report_id}`: `{param.type}`.',
            )

        if param.type in CHOICES_PARAM_TYPE and not param.choices:
            errors.append(f'Missing choices for parameter `{param.id}` on report `{report_id}`.')

    diff = set(_get_duplicates(params_ids))
    if diff:
        errors.append(
            f'The following parameter ids are duplicated on report `{report_id}`: {",".join(diff)}',
        )
    return errors


def _validate_renderer(report_id, renderer):

    errors = []
    if renderer.type not in get_renderers():
        errors.append(
            f'renderer `{renderer.id}` of type `{renderer.type}` is not known on `{report_id}`.',
        )
        return errors

    renderer_cls = get_renderer_class(renderer.type)
    errors.extend(renderer_cls.validate(renderer))
    return errors


def _validate_report(report):
    errors = []
    if not os.path.isfile(
        os.path.join(report.root_path, report.readme_file),
    ):
        errors.append(
            f'report `{report.local_id}` property `readme_file` cannot be resolved to a file.',
        )

    tokens = report.entrypoint.split('.')
    if len(tokens) < 2:
        errors.append(
            f'entrypoint `{report.entrypoint}` does not follow the package structure.',
        )
        return errors

    report_root = os.path.join(report.root_path, tokens[0], tokens[1])
    if not (os.path.isdir(report_root) or os.path.isfile(f'{report_root}.py')):
        errors.append(
            f'entrypoint `{report.entrypoint}` directory structure '
            'does not match the package definition.',
        )

    errors.extend(_validate_parameters(report.local_id, report.parameters))

    renderers_ids = []
    default_renderers = []
    for renderer in report.renderers:
        if renderer.default:
            default_renderers.append(renderer.id)
        renderers_ids.append(renderer.id)
        errors.extend(_validate_renderer(report.local_id, renderer))

    diff = set(_get_duplicates(renderers_ids))
    if diff:
        errors.append(f'report {report.local_id} has duplicated renderer ids: {",".join(diff)}')

    if len(default_renderers) > 1:
        errors.append(
            f'report {report.local_id} has multiple default renderers: '
            f'{",".join(default_renderers)}',
        )

    return errors


def validate(repo):
    errors = []
    if not os.path.isfile(
        os.path.join(repo.root_path, repo.readme_file),
    ):
        errors.append(
            'repository property `readme_file` cannot be resolved to a file.',
        )

    reports_local_ids = []
    for report in repo.reports:
        reports_local_ids.append(report.local_id)
        errors.extend(_validate_report(report))

    diff = set(_get_duplicates(reports_local_ids))
    if diff:
        errors.append(
            f'Multiple reports within single module found: {",".join(diff)}',
        )

    return errors
