# How to run the UI

We set this up so it is hosted as a huggingface space. Each commit to `main` triggers a push and a rebuild on their servers.

For local testing, assuming you have all the required packages installed in a
conda env or virtualenv, and that env is activated:

```bash
cd src
streamlit run main.py
```
Then use a web browser to view the site indiciated, by default: http://localhost:8501

# How to build and view docs locally

We have a CI action to present the docs on github.io. 
To validate locally, you need the deps listed in `requirements.txt` installed. 

Run
```bash
mkdocs serve
```

And navigate to the wish server running locally, by default: http://127.0.0.1:8888/

This automatically watches for changes in the markdown files, but if you edit the 
something else like the docstrings in py files, triggering a rebuild in another terminal
refreshes the site, without having to quit and restart the server.

```bash
mkdocs build -c
```



# Set up a venv

(standard stuff)

# Set up a conda env

(Standard stuff)


# Testing

## use of markers

The CI runs with `--strict-markers` so any new marker must be registered in
`pytest.ini`. 

- the basic CI action runs the fast tests only, skipping all tests marked
  `visual` and `slow`
- the CI action on PR runs the `slow` tests, but still excluding `visual`. 
- a second action for the visual tests runs on PR.

Check all tests are marked ok, and that they are filtered correctly by the 
groupings used in CI:
```bash
pytest --collect-only -m "not slow and not visual" --strict-markers --ignore=tests/visual_selenium
pytest --collect-only -m "not visual" --strict-markers --ignore=tests/visual_selenium
pytest --collect-only -m "visual" --strict-markers tests/visual_selenium/ -s --demo
```



## local testing
To run the tests locally, we have the standard dependencies of the project, plus the test runner dependencies. 

```bash
pip install -r tests/requirements.txt
```

(If we migrate to using toml config, the test reqs could be consolidated into an optional section)


**Running tests**
from the project root, simply run:

```bash
pytest
# or pick a specific test file to run
pytest tests/test_whale_viewer.py
```

To generate a coverage report to screen (also run the tests):
```bash
pytest --cov=src 
```

To generate reports on pass rate and coverage, to files:
```bash
pytest --junit-xml=test-results.xml
pytest --cov-report=lcov --cov=src
```

## local testing for visual tests 

We use seleniumbase to test the visual appearance of the app, including the
presence of elements that appear through the workflow.  This testing takes quite
a long time to execute. It is configured in a separate CI action
(`python-visualtests.yml`).

```bash
# install packages for app and for visual testing
pip install ./requirements.txt
pip install -r tests/visual_selenium/requirements_visual.txt
```

**Running tests**
The execution of these tests requires that the site/app is running already, which
is handled by a fixture (that starts the app in another thread).

Alternatively, in one tab, run: 
```bash
streamlit run src/main.py
```

In another tab, run:
```bash
# run just the visual tests
pytest -m "visual" --strict-markers
# run in demo mode, using firefox (default is chrome)
pytest -m "visual" --strict-markers -s browser=firefox --demo

# the inverse set:
pytest -m "not slow and not visual" --strict-markers --ignore=tests/visual_selenium

```



## CI testing

Initially we have an action setup that runs all tests in the `tests` directory, within the `test/tests` branch.

TODO: Add some test report & coverage badges to the README.


## Environment flags used in development 

- `DEBUG_AUTOPOPULATE_METADATA=True` : Set this env variable to have the text
  inputs autopopulated, to make stepping through the workflow faster during
  development work.

Typical usage:

```bash
DEBUG_AUTOPOPULATE_METADATA=True streamlit run src/main.py
```

