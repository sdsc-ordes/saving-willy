import pytest
from pathlib import Path

from whale_viewer import format_whale_name

# testing format_whale_name
# - testing with valid whale names
# - testing with invalid whale names
# - empty string
# - with the wrong datatype

def test_format_whale_name_ok():
    # some with 1 word, most with 2 words, others with 3 or 4.
    assert format_whale_name("right_whale") == "Right Whale"
    assert format_whale_name("blue_whale") == "Blue Whale"
    assert format_whale_name("humpback_whale") == "Humpback Whale"
    assert format_whale_name("sperm_whale") == "Sperm Whale"
    assert format_whale_name("fin_whale") == "Fin Whale"
    assert format_whale_name("sei_whale") == "Sei Whale"
    assert format_whale_name("minke_whale") == "Minke Whale"
    assert format_whale_name("gray_whale") == "Gray Whale"
    assert format_whale_name("bowhead_whale") == "Bowhead Whale"
    assert format_whale_name("beluga") == "Beluga"

    assert format_whale_name("long_finned_pilot_whale") == "Long Finned Pilot Whale"
    assert format_whale_name("melon_headed_whale") == "Melon Headed Whale"
    assert format_whale_name("pantropic_spotted_dolphin") == "Pantropic Spotted Dolphin"
    assert format_whale_name("spotted_dolphin") == "Spotted Dolphin"
    assert format_whale_name("killer_whale") == "Killer Whale"


def test_format_whale_name_invalid():
    # not so clear what this would be, except perhaps a string that has gone through the fucn alrealdy?
    assert format_whale_name("Right Whale") == "Right Whale"
    assert format_whale_name("Blue Whale") == "Blue Whale"
    assert format_whale_name("Long Finned Pilot Whale") == "Long Finned Pilot Whale"

# testing with empty string
def test_format_whale_name_empty():
    assert format_whale_name("") == ""
    
# testing with the wrong datatype
def test_format_whale_name_none():
    with pytest.raises(TypeError):
        format_whale_name(None)
        

# display_whale requires UI to test it. 
