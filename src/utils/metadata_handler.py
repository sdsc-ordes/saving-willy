import streamlit as st

def metadata2md(image_hash:str, debug:bool=False) -> str:
    """Get metadata from cache and return as markdown-formatted key-value list

    Args:
        image_hash (str): The hash of the image to get metadata for
        debug (bool, optional): Whether to print additional fields.
        
    Returns:
        str: Markdown-formatted key-value list of metadata
        
    """
    markdown_str = "\n"
    keys_to_print = ["author_email", "latitude", "longitude", "date", "time"]
    if debug:
        keys_to_print += ["image_md5", "selected_class", "top_prediction", "class_overriden"]

    observation = st.session_state.public_observations.get(image_hash, {})
    
    for key, value in observation.items():
        if key in keys_to_print:
            markdown_str += f"- **{key}**: {value}\n"

    return markdown_str

