# Contributing to the Central Dogma Client

First of all, thank you so much for taking your time to visit centraldogma-python.
Here, everything you do or even your mere presence is a contribution in a broad sense.
We strongly believe your contribution will enrich our community and create
a virtuous cycle that propels the project into something great.

## Install

```
$ uv pip install -e ".[dev]"
```

## Code generation

This project uses `unasync` to automatically generate all synchronous (sync) client code from its asynchronous (async) counterpart.

As a contributor, you must not edit the generated synchronous code (e.g., files directly under `centraldogma/_sync/`) by hand.
All changes must be made to the asynchronous source files, which are located in the centraldogma/_async/ directory.
After you modify any code in `centraldogma/_async/`, you must run the code generation script to update the synchronous code:

```
$ python utils/run-unasync.py
```

This command regenerates the synchronous code based on your changes.
You must include both your original changes (in `centraldogma/_async/`) and the newly generated synchronous files in your Pull Request.

## Running tests locally

### Unit test

```
$ pytest
```

### Integration test

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

## Lint

- [PEP 8](https://www.python.org/dev/peps/pep-0008)
    ```
    $ black .
    ```

## Documentation

- [PEP 257](https://www.python.org/dev/peps/pep-0257)

### To build sphinx at local

```
$ pip install sphinx sphinx_rtd_theme
$ cd docs && make html
```
