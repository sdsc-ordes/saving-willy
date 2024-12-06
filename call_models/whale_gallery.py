from itertools import cycle
import streamlit as st

import whale_viewer as sw_wv

def render_whale_gallery(n_cols:int = 4):
    """
    A function to display a gallery of whale images in a grid
    """
    def format_whale_name(name):
        return name.replace("_", " ").capitalize()
    
    # make a grid of images, use some css to get more uniform
    # https://discuss.streamlit.io/t/grid-of-images-with-the-same-height/10668/12
    # nb: I think there are some community components, need to investigate their usage
    st.markdown(
    """
<style>

    .st-key-swgallery div[data-testid="stVerticalBlock"] {
        justify-content: center;
    }
    .st-key-swgallery div[data-testid="stVerticalBlockBorderWrapper"] {
        display: flex !important;
        min-height: 185px !important; //185 for image+caption or 255 with link
        align-items: center;
        //background-color: darkgreen;
    }


/*
    .st-key-swheader div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: lightgreen;
        min-height: 16px !important;
        border: 1px solid #ccc;
    }
*/
    .st-key-swgallery div[data-testid="stColumn"] {
        flex: 1 !important; /* additionally, equal width */
        padding: 1em !important;
        align-items: center;
        border: solid !important;
        border-radius: 0px !important;
        max-width: 220px !important;
        border-color: #0000 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)
    
    cols = cycle(st.columns(n_cols)) 
    for ix in range(len(sw_wv.df_whale_img_ref)):
        img_name = sw_wv.df_whale_img_ref.iloc[ix].loc["WHALE_IMAGES"]
        whale_name = format_whale_name(str(sw_wv.df_whale_img_ref.iloc[ix].name))
        url = sw_wv.df_whale_img_ref.iloc[ix].loc['WHALE_REFERENCES']
        image_path = f"images/references/{img_name}"
        #next(cols).image(image_path, width=150, caption=f"{whale_name}")
        thing = next(cols)
        with thing:
            with st.container(border=True):
                # using the caption for name is most compact but no link.
                #st.image(image_path, width=150, caption=f"{whale_name}")
                st.image(image_path, width=150)
                #st.markdown(f"[{whale_name}]({url})" ) # doesn't seem to allow styling, just do in raw html:w
                html = f"<div style='text-align: center; font-size: 14px'><a href='{url}'>{whale_name}</a></div>"
                st.markdown(html, unsafe_allow_html=True)
                

        #next(cols).image(image_path, width=150, caption=f"{whale_name}")

    
if __name__ == "__main__":
    ''' example usage, with some other elements to help illustrate how 
    streamlit keys can be used to target specific css properties 
    '''
    # define a container just to hold a couple of elements
    header_cont = st.container(key='swheader')
    with header_cont:
        c1, c2 = st.columns([2, 3])
        c1.markdown('left')
        c2.button("Refresh Gallery (noop)")
    # here we make a container to allow filtering css properties 
    # specific to the gallery (otherwise we get side effects)
    tg_cont = st.container(key="swgallery")
    with tg_cont:
        render_whale_gallery(n_cols=4)
    
    pass