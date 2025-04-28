import streamlit as st
import json 
from PIL import Image


def hotdog_classify(pipeline_hot_dog, tab_hotdogs): 
    col1, col2 = tab_hotdogs.columns(2)
    for file in st.session_state.files:
        image = st.session_state.images[file.name]
        observation = st.session_state.observations[file.name].to_dict()
        # display the image (use cached version, no need to reread)
        col1.image(image, use_column_width=True)
        # and then run inference on the image
        hotdog_image = Image.fromarray(image)
        predictions = pipeline_hot_dog(hotdog_image)

        col2.header("Probabilities")
        first = True
        for p in predictions:
            col2.subheader(f"{ p['label'] }: { round(p['score'] * 100, 1)}%")
            if first:
                observation['predicted_class'] = p['label']
                observation['predicted_score'] = round(p['score'] * 100, 1)
                first = False
        
        tab_hotdogs.write(f"Session observation: {json.dumps(observation)}")