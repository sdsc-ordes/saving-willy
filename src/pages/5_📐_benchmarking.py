import streamlit as st

st.set_page_config(
    page_title="Benchmarking",
    page_icon="📐",
    layout="wide",
)

st.title("Benchmark of ML models")

st.write("All credits go to the original Leaderboard on hugging face: https://huggingface.co/spaces/opencompass/opencompass-llm-leaderboard"
)
st.write("This image serves as a pure placeholder to illustrate benchmarking possibilities.")

st.image("src/images/design/leaderboard.png", caption="Benchmarking models")