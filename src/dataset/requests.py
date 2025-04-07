import streamlit as st
import pandas as pd
from dataset.cleaner import clean_lat_long, clean_date
from dataset.download import get_dataset
from dataset.fake_data import generate_fake_data

def default_data_view(): 
    df = get_dataset()
    df = generate_fake_data(df, 100)
    df = clean_lat_long(df)
    df = clean_date(df)
    return df

def filter_data(df): 
    if st.session_state.date_range: 
        df_filtered = df[
        (df['date'] >= pd.to_datetime(st.session_state.date_range[0])) & \
            (df['date'] <= pd.to_datetime(st.session_state.date_range[1]))
        ]
    if st.session_state.lon_range:
        df_filtered = df[
        (df['lon'] >= st.session_state.lon_range[0]) & \
            (df['lon'] <= st.session_state.lon_range[1])
        ]
    if st.session_state.lat_range:
        df_filtered = df[
        (df['lat'] >= st.session_state.lat_range[0]) & \
            (df['lat'] <= st.session_state.lat_range[1])
        ]
    return df_filtered

def show_specie_author(df): 
    df = df.groupby(['species', 'author_email']).size().reset_index(name='counts')
    for specie in df["species"].unique(): 
        st.subheader(f"Species: {specie}")
        specie_data = df[df['species'] == specie]
        for _, row in specie_data.iterrows():
            key = f"{specie}_{row['author_email']}"
            label = f"{row['author_email']} ({row['counts']})"
            st.session_state.checkbox_states[key] = st.checkbox(label, key=key)

def show_new_data_view(df): 
    df = filter_data(df)
    df_ordered = show_specie_author(df)
    return df_ordered

    
    
    

