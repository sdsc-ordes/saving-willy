import pandas as pd 

def clean_lat_long(df) -> pd.DataFrame:  
    """
    Clean latitude and longitude columns in the DataFrame.
    Ensure lat and lon are numeric, coerce errors to NaN
    Args:
        df (pd.DataFrame): DataFrame containing latitude and longitude columns.
    Returns:
        pd.DataFrame: DataFrame with cleaned latitude and longitude columns.
    """
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')

    # Drop rows with NaN in lat or lon
    df = df.dropna(subset=['lat', 'lon']).reset_index(drop=True)
    return df

def clean_date(df) -> pd.DataFrame: # Ensure lat and lon are numeric, coerce errors to NaN
    """
    Clean date column in the DataFrame.
    Args:
        df (pd.DataFrame): DataFrame containing date column.
    Returns:
        pd.DataFrame: DataFrame with cleaned date column.
    """
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    # Drop rows with NaN in lat or lon
    df = df.dropna(subset=['date']).reset_index(drop=True)
    return df