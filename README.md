# Connect Reports Core

![pyversions](https://img.shields.io/pypi/pyversions/connect-reports-core.svg) [![Build Connect Reports Core](https://github.com/cloudblue/connect-reports-core/actions/workflows/build.yml/badge.svg)](https://github.com/cloudblue/connect-reports-core/actions/workflows/build.yml)[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=connect-reports-core&metric=alert_status)](https://sonarcloud.io/dashboard?id=connect-reports-core) [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=connect-reports-core&metric=coverage)](https://sonarcloud.io/dashboard?id=connect-reports-core) [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=connect-reports-core&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=connect-reports-core)

## Introduction

`Connect Reports Core` is the kernel package for handling reports on CloudBlue Connect Ecosystem. This library is reponsible to validate reports definition, to choose render for parsing process and to write results of the report execution.


## Install

`Connect Reports Core` requires python 3.8 or later and has the following dependencies:

* openpyxl>=2.5.14
* WeasyPrint>=52.2
* Jinja2>=2.11.3
* jsonschema<=3.2.0
* pytz>=2021.1
* lxml>=4.6.2

`Connect Reports Core` can be installed from [pypi.org](https://pypi.org/project/connect-reports-core/) using pip:

```
$ pip install connect-reports-core
```


## License

``Connect Reports Core`` is released under the [Apache License Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).
