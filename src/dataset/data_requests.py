import streamlit as st
import pandas as pd
from dataset.cleaner import clean_lat_long, clean_date
from dataset.download import get_dataset
from dataset.fake_data import generate_fake_data

def data_prep() -> pd.DataFrame: 
    """
    Prepares the dataset for use in the application.
    Downloads the dataset and cleans the data (and generates fake data if needed).
    Returns:
        pd.DataFrame: A DataFrame containing the cleaned dataset.
    """
    df = get_dataset()
    # uncomment to generate some fake data 
    # df = generate_fake_data(df, 100)
    df = clean_lat_long(df)
    df = clean_date(df)
    return df

def filter_data(df:pd.DataFrame) -> pd.DataFrame: 
    """
    Filter the DataFrame based on user-selected ranges for latitude, longitude, and date.
    Args:
        df (pd.DataFrame): DataFrame to filter.
    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    df_filtered = df[
    (df['date'] >= pd.to_datetime(st.session_state.date_range[0])) & 
        (df['date'] <= pd.to_datetime(st.session_state.date_range[1])) &
    (df['lon'] >= st.session_state.lon_range[0]) & 
        (df['lon'] <= st.session_state.lon_range[1]) &
    (df['lat'] >= st.session_state.lat_range[0]) & 
        (df['lat'] <= st.session_state.lat_range[1])
    ]
    return df_filtered

def show_specie_author(df:pd.DataFrame): 
    """
    Display a list of species and their corresponding authors with checkboxes.
    Args:
        df (pd.DataFrame): DataFrame containing species and author information.
    """
    df = df.groupby(['species', 'author_email']).size().reset_index(name='counts')
    for specie in df["species"].unique(): 
        st.subheader(f"Species: {specie}")
        specie_data = df[df['species'] == specie]
        for _, row in specie_data.iterrows():
            key = f"{specie}_{row['author_email']}"
            label = f"{row['author_email']} ({row['counts']})"
            st.session_state.checkbox_states[key] = st.checkbox(label, key=key)

def show_new_data_view(df:pd.DataFrame) -> pd.DataFrame: 
    """
    Show the new filtered data view on the UI.
    Filter the dataframe based on the state of the localisation sliders and selected timeframe by the user.
    Then, show the results of the filtering grouped by species then by authors. 
    Authors are matched to a checkbox component so the user can click it if he/she/they wish to request data from this author.
    Args:
        df (pd.DataFrame): DataFrame to filter and display.
    Returns:
        pd.DataFrame: Filtered and grouped DataFrame.
    """
    df = filter_data(df)
    df_ordered = show_specie_author(df)
    return df_ordered

    
    
    

