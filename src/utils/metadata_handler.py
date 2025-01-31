import streamlit as st

def metadata2md(image_hash:str) -> str:
    """Get metadata from cache and return as markdown-formatted key-value list

    Args:
        image_hash (str): The hash of the image to get metadata for
        
    Returns:
        str: Markdown-formatted key-value list of metadata
        
    """
    markdown_str = "\n"
    keys_to_print = ["author_email", "latitude", "longitude", "date", "time"]

    observation = st.session_state.public_observations.get(image_hash, {})
    
    for key, value in observation.items():
        if key in keys_to_print:
            markdown_str += f"- **{key}**: {value}\n"

    return markdown_str

