# Main entry point 

This module sets up the streamlit UI frontend, 
as well as logger and session state elements in the backend.

The session state is used to retain values from one interaction to the next, since the streamlit execution model is to re-run the entire script top-to-bottom upon each user interaction (e.g. click). 
See streamlit [docs](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state).


::: src.entry_and_hotdog