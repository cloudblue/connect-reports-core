# Connect Reports Core

![pyversions](https://img.shields.io/pypi/pyversions/connect-reports-core.svg) [![PyPi Status](https://img.shields.io/pypi/v/connect-reports-core.svg)](https://pypi.org/project/connect-reports-core/) [![Build Connect Reports Core](https://github.com/cloudblue/connect-reports-core/actions/workflows/build.yml/badge.svg)](https://github.com/cloudblue/connect-reports-core/actions/workflows/build.yml) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=cloudblue_connect-reports-core&metric=alert_status)](https://sonarcloud.io/dashboard?id=cloudblue_connect-reports-core) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=cloudblue_connect-reports-core&metric=coverage)](https://sonarcloud.io/dashboard?id=cloudblue_connect-reports-core) [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=cloudblue_connect-reports-core&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=cloudblue_connect-reports-core)

## Introduction

`Connect Reports Core` is the kernel package for handling reports on CloudBlue Connect Ecosystem. 
This library is reponsible for validation of reports definition, choosing of renderer for parsing process and writing results of reports execution.


## Install

`Connect Reports Core` requires python 3.9 or later and has the following dependencies:

* openpyxl >=2.5.14
* WeasyPrint >=59,<64
* Jinja2 >=2,<4
* jsonschema >=3,<5
* pytz *
* lxml >=4.9
* orjson >=3.5.2,<4
* plotly >=5.9.0,<6
* kaleido >=0.4,<1
`Connect Reports Core` can be installed from [pypi.org](https://pypi.org/project/connect-reports-core/) using pip:

```
$ pip install connect-reports-core
```

## Testing

On MacOs:
* Install system dependencies
```commandline
brew install py3cairo pango
```
* Create virtualenv
* Install project dependencies
```commandline
pip install poetry
poetry update
```
* Run tests
```commandline
poetry run pytest
```


## License

``Connect Reports Core`` is released under the [Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
