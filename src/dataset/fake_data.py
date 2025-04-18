import pandas as pd
import random
from datetime import datetime, timedelta

from dataset.download import presentation_data_schema
from whale_viewer import WHALE_CLASSES

def generate_fake_data(df, num_fake) -> pd.DataFrame:
    """
    Generate fake data for the dataset.

    Args:
        df (pd.DataFrame): Original DataFrame to append fake data to.
        num_fake (int): Number of fake observations to generate.
    Returns:
        pd.DataFrame: DataFrame with the original and fake data.
    """

    # Options for random generation
    species_options = WHALE_CLASSES
    email_options = [
        'dr.marine@oceanic.org', 'whale.research@deepblue.org',
        'observer@sea.net', 'super@whale.org'
    ]

    def random_ocean_coord():
        """Generate random ocean-friendly coordinates."""
        lat = random.uniform(-60, 60)  # avoid poles
        lon = random.uniform(-180, 180)
        return lat, lon

    def random_date(start_year=2018, end_year=2025):
        """Generate a random date."""
        start = datetime(start_year, 1, 1)
        end = datetime(end_year, 1, 1)
        return start + timedelta(days=random.randint(0, (end - start).days))

    new_data = []
    for _ in range(num_fake):
        lat, lon = random_ocean_coord()
        species = random.choice(species_options)
        email = random.choice(email_options)
        date = random_date()
        new_data.append([lat, lon, species, email, date])

    new_df = pd.DataFrame(new_data, columns=presentation_data_schema).astype(presentation_data_schema)
    df = pd.concat([df, new_df], ignore_index=True)
    return df