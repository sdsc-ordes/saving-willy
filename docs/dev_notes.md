# How to run the UI

We set this up so it is hosted as a huggingface space. Each commit to `main` triggers a push and a rebuild on their servers.

For local testing, assuming you have all the required packages installed in a
conda env or virtualenv, and that env is activated:

```
cd src
streamlit run main.py
```
Then use a web browser to view the site indiciated, by default: http://localhost:8501

# How to build and view docs locally

We have a CI action to presesnt the docs on github.io. 
To validate locally, you need the deps listed in `requirements.txt` installed. 

Run
```
mkdocs serve
```
And navigate to the wish server running locally, by default: http://127.0.0.1:8888/

This automatically watches for changes in the markdown files, but if you edit the 
something else like the docstrings in py files, triggering a rebuild in another terminal
refreshes the site, without having to quit and restart the server.
```
mkdocs build -c
```



# Set up a venv

(standard stuff)

# Set up a conda env

(Standard stuff)