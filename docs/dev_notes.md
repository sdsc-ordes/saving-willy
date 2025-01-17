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

We have a CI action to presesnt the docs on github.io. 
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


## CI testing

Initially we have an action setup that runs all tests in the `tests` directory, within the `test/tests` branch.

TODO: Add some test report & coverage badges to the README.
