import pandas as pd 

def clean_lat_long(df): # Ensure lat and lon are numeric, coerce errors to NaN
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')

    # Drop rows with NaN in lat or lon
    df = df.dropna(subset=['lat', 'lon']).reset_index(drop=True)
    return df

def clean_date(df): # Ensure lat and lon are numeric, coerce errors to NaN
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    # Drop rows with NaN in lat or lon
    df = df.dropna(subset=['date']).reset_index(drop=True)
    return df