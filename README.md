# Central Dogma client in Python
Python client library for Central Dogma

## Install
```
$ pip install -r requirements.txt
$ pip install --user .
```

## Usage
### Getting started
Please see [`examples` folder](https://github.com/line/centraldogma-python/tree/main/examples) for more detail.
```python
client = ApiClient(base_url, token, timeout=30)
client.list_projects()
...
```

## Development
### Install
```
$ pip install -r requirements-dev.txt
```

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
$ INTEGRATION_TEST=1 pytest
```

3. Stop the server
```
$ docker-compose down
```

### Lint
```
$ black .
```

### Documentation
- [PEP 257](https://www.python.org/dev/peps/pep-0257)
