import streamlit as st

st.set_page_config(
    page_title="Challenges",
    page_icon="🏆",
    layout="wide",
)

st.title("Research Challenges (Kaggle)")

st.write("Working together to innovate is essential. Here are the current and past challenges on Kaggle organized around cetacean conservation.")

st.link_button("Click here for the full challenge.",
               url = "https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.kaggle.com/competitions/happy-whale-and-dolphin&ved=2ahUKEwiIoPjCicaMAxVrzgIHHaDYH6MQFnoECAoQAQ&usg=AOvVaw3Cl2cK7ZwU_jTyDeA5Yg1m"
               )
st.image("src/images/design/challenge2.png",
    caption=  "Ted Cheeseman, Ken Southerland, Walter Reade, and Addison Howard. Happywhale - Whale and Dolphin Identification. https://kaggle.com/competitions/happy-whale-and-dolphin, 2022. Kaggle.")


st.link_button("Click here for the full challenge.",
                url="https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.kaggle.com/competitions/humpback-whale-identification&ved=2ahUKEwiIoPjCicaMAxVrzgIHHaDYH6MQFnoECB8QAQ&usg=AOvVaw0IdiKQC3GpODtI-fBt-yV3"
                )
st.image("src/images/design/challenge1.png",
    caption ="Addison Howard, inversion, Ken Southerland, and Ted Cheeseman. Humpback Whale Identification. https://kaggle.com/competitions/humpback-whale-identification, 2018. Kaggle.")
