import streamlit as st

def metadata2md() -> str:
    """Get metadata from cache and return as markdown-formatted key-value list

    Returns:
        str: Markdown-formatted key-value list of metadata
        
    """
    markdown_str = "\n"
    keys_to_print = ["latitude","longitude","author_email","date","time"]
    for key, value in st.session_state.public_observation.items():
            if key in keys_to_print:
                markdown_str += f"- **{key}**: {value}\n"
    return markdown_str

