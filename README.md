# Central Dogma client in Python
<a href="https://pypi.org/project/centraldogma-python/">
    <img src="https://badge.fury.io/py/centraldogma-python.svg" alt="Package version">
</a>

Python client library for Central Dogma

🚧 WIP - Initial development is in progress 🚧

## Install
```
$ pip install centraldogma
```

## Getting started
```pycon
>>> from centraldogma.dogma import Dogma
>>> dogma = Dogma("https://dogma.yourdomain.com", "token")
>>> dogma.list_projects()
[]
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
