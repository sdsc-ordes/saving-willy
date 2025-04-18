import streamlit as st

st.set_page_config(
    page_title="About",
    page_icon="🐋",
)

st.markdown(
    """
# About
    We created this web app in [a hackathon](https://sdsc-hackathons.ch/projectPage?projectRef=vUt8BfDJXaAs0UfOesXI|XyWLFpqjq3CX3zrM4uz8). 
    
    This interface is a Proof of Concept of a Community-driven Research Data Infrastructure for the Cetacean Conservation Community. 

    Please reach out on [the project Github issues](https://github.com/sdsc-ordes/saving-willy/issues) for feedback, suggestions, or if you want to join the project.

# Open Source Resources

## UI Code
    - The [space is hosted on Hugging Face](https://huggingface.co/spaces/Saving-Willy/saving-willy-space). 
    - The [UI code is available on Github](https://github.com/sdsc-ordes/saving-willy).
    - The [development space](https://huggingface.co/spaces/Saving-Willy/saving-willy-dev) is also hosted publically on Hugging Face.

## The Machine Learning Models
    - The [model](https://huggingface.co/Saving-Willy/cetacean-classifier) is hosted on Hugging Face.
    - The [original Kaggle model code](https://github.com/knshnb/kaggle-happywhale-1st-place) is open on Github as well. 

## The Data

(temporary setup, a more stable database is probably desired.)
    - The dataset is hosted on Hugging Face.
    - The [dataset syncing code](https://github.com/vancauwe/saving-willy-data-sync) is available on Github. 

# Credits and Thanks 

## Developers
- [Rob Mills](https://github.com/rmm-ch)
- [Laure Vancauwenberghe](https://github.com/vancauwe)

## Special Thanks
- [EDMAKTUB](https://edmaktub.org) for their advice. 
- [Swiss Data Science Center](https://www.datascience.ch) for [the hackathon that started the project](https://sdsc-hackathons.ch/projectPage?projectRef=vUt8BfDJXaAs0UfOesXI|XyWLFpqjq3CX3zrM4uz8).
- [HappyWhale](https://happywhale.com) for launching [the Kaggle challenge that led to model development](https://www.kaggle.com/competitions/happy-whale-and-dolphin).

"""
)