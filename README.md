# Central Dogma client in Python

[![PyPI version](https://badge.fury.io/py/centraldogma-python.svg)](https://badge.fury.io/py/centraldogma-python)
[![PyPI Supported Python Versions](https://img.shields.io/pypi/pyversions/centraldogma-python.svg)](https://pypi.python.org/pypi/centraldogma-python/)
[![check](https://github.com/line/centraldogma-python/actions/workflows/test.yml/badge.svg)](https://github.com/line/centraldogma-python/actions/workflows/test.yml)
[![Downloads](https://static.pepy.tech/badge/centraldogma-python/month)](https://pepy.tech/project/centraldogma-python)

Python client library for [Central Dogma](https://line.github.io/centraldogma/).

## Install

```
$ pip install centraldogma-python
```

## Getting started

Only URL indicating CentralDogma server and access token are required.
```pycon
>>> from centraldogma.dogma import Dogma
>>> dogma = Dogma("https://dogma.yourdomain.com", "token")
>>> dogma.list_projects()
[]
```

It supports client configurations.
```pycon
>>> retries, max_connections = 5, 10
>>> dogma = Dogma("https://dogma.yourdomain.com", "token", retries=retries, max_connections=max_connections)
```

Please see [`examples` folder](https://github.com/line/centraldogma-python/tree/main/examples) for more detail.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md)