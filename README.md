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

---

## Development
### Tests
#### Unit test
```
$ pytest
```

#### Integration test
1. Run local Central Dogma server with docker-compose
    ```
    $ docker-compose up -d
    ```

2. Run integration tests
    ```
    $ INTEGRATION_TEST=true pytest
    ```

3. Stop the server
    ```
    $ docker-compose down
    ```

### Lint
- [PEP 8](https://www.python.org/dev/peps/pep-0008)
    ```
    $ black .
    ```

### Documentation
- [PEP 257](https://www.python.org/dev/peps/pep-0257)

#### To build sphinx at local
```
$ pip install sphinx sphinx_rtd_theme
$ cd docs && make html
```
