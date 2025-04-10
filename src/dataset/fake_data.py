import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

def generate_fake_data(df, num_fake):
    """
    Generate fake data for the dataset.
    Args:
        df (pd.DataFrame): Original DataFrame to append fake data to.
        num_fake (int): Number of fake observations to generate.
    Returns:
        pd.DataFrame: DataFrame with the original and fake data.
    """

    # Options for random generation
    species_options = [
        "beluga",
        "blue_whale",
        "bottlenose_dolphin",
        "brydes_whale",
        "commersons_dolphin",
        "common_dolphin",
        "cuviers_beaked_whale",
        "dusky_dolphin",
        "false_killer_whale",
        "fin_whale",
        "frasiers_dolphin",
        "gray_whale",
        "humpback_whale",
        "killer_whale",
        "long_finned_pilot_whale",
        "melon_headed_whale",
        "minke_whale",
        "pantropic_spotted_dolphin",
        "pygmy_killer_whale",        
        "rough_toothed_dolphin",
        "sei_whale",
        "short_finned_pilot_whale",
        "southern_right_whale",
        "spinner_dolphin",
        "spotted_dolphin",
        "white_sided_dolphin",
    ]
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

    new_df = pd.DataFrame(new_data, columns=['lat', 'lon', 'species', 'author_email', 'date'])
    df = pd.concat([df, new_df], ignore_index=True)
    return df