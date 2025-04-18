import streamlit as st
import os

import logging

st.set_page_config(
    page_title="Home",
    page_icon="🐳",
)

# get a global var for logger accessor in this module
LOG_LEVEL = logging.DEBUG
g_logger = logging.getLogger(__name__)
g_logger.setLevel(LOG_LEVEL)

# one toggle for all the extra debug text
if "MODE_DEV_STATEFUL" not in st.session_state:
    st.session_state.MODE_DEV_STATEFUL = False
    
from utils.st_logs import init_logging_session_states
init_logging_session_states() # logging init should be early 

# set email state var to exist, to permit persistence across page switches 
if "input_author_email" not in st.session_state:
    st.session_state.input_author_email = ""

st.write("""
         # Welcome ! 🐬˚✧˚.⋆🐋

         # Cetacean Conservation Community
        """)

st.sidebar.success("Explore the pages: there are machine learning models, data requests, maps and more !")
st.sidebar.image(
    "src/images/logo/sdsc-horizontal.png",
    width=200
)

st.markdown(
    """
    ## 💙 Research Data Infrastructure

    ˖°𓇼🌊⋆🐚🫧 This interface is a Proof of Concept of a Community-driven Research Data Infrastructure (RDI) for the Cetacean Conservation Community. 
    This PoC will happily be made into a production-ready RDI if the community is interested.

    👤 The intended users of this interface are the researchers and conservationists working on cetacean conservation. 
    In its current state, the interface is designed to be user-friendly, allowing users to upload images of cetaceans and receive species classification results.

    🤝 We value community-contributions and encourage anyone interested to reach out on [the main repository's Github issues](https://github.com/sdsc-ordes/saving-willy/issues).
    
    🌍 The goal of this RDI is to explore community methods for sharing code and data. 
    

    ## 💻 Sharing Code

    Through the platform of Hugging Face 🤗, machine learning models are published so they can be used for inference on this UI or by other users. 
    Currently, a demonstration model is available for cetacean species classification. 
    The model is based on the [HappyWhale](https://www.kaggle.com/competitions/happy-whale-and-dolphin) competition with the most recent weights. 
    Since part of the model was not made public, the classifier should not be used for inference and is purely demonstrative. 
    
    🏆 Ideally, through new Kaggle challenges or ongoing development in research groups, new models can be brought to Hugging Face and onto the UI.
    

    ## 💎 Sharing Data 

    The dataset is hosted on Hugging Face 🤗 as well, in order to share the metadata of the images which have been classified by the model. 
    Making the metadata public is under the choice of th researcher, who can choose to use the model for inference without making the image metadata public afterwards. 
    Of course, we encourage open data. Please note that the original images are never made public in the current-state RDI. 

    💪 The RDI also explore how to share data after inference, with a simple data request page where researchers can fitler the existing metadata from the Hugging Face dataset, and then easily select those of interest for them. 
    Ideally, the Request button would either start a Discord channel discussion between concerned parties of the data request, or generate an e-mail with interested parties. This design is still under conception.

"""
)




g_logger.info("App started.")
g_logger.warning(f"[D] Streamlit version: {st.__version__}. Python version: {os.sys.version}")

#g_logger.debug("debug message")
#g_logger.info("info message")
#g_logger.warning("warning message")
