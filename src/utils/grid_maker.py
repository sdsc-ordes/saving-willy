import streamlit as st
import math

def gridder(items):
    """Creates a grid for displaying items in a batched manner.
    Args:
        items (list): The items to be displayed.
    Returns:
        batch_size (int): The number of items to display in each batch.
        row_size (int): The number of items to display in each row.
        page (int): The range of pages available based on the number of items.
    """
    cols = st.columns(3)
    with cols[0]:
        batch_size = st.select_slider("Batch size:",range(10,110,10), value=10)
    with cols[1]:
        row_size = st.select_slider("Row size:", range(1,6), value = 5)
    num_batches = math.ceil(len(items)/batch_size)
    with cols[2]:
        page = st.selectbox("Page", range(1,num_batches+1))
    return batch_size, row_size, page