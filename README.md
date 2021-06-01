# Central Dogma client in Python
Python client library for Central Dogma

## Install
```
$ pip install -r requirements.txt
$ pip install --user .
```

## Usage
### Getting started
Please see [`examples` folder](https://github.com/hexoul/centraldogma-python/tree/main/examples) for more detail.
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

### Test
```
$ pytest
```

### Lint
```
$ black .
```

### Documentation
- [PEP 257](https://www.python.org/dev/peps/pep-0257)
