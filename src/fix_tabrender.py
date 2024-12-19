import streamlit as st

# code for fixing the issue with streamlit tabs rendering height 0 when not active
# https://github.com/streamlit/streamlit/issues/7376 
# 
# see also https://github.com/randyzwitch/streamlit-folium/issues/128, got
#   closed becasue it is apparently a st.tabs problem


import uuid, html
# workaround for streamlit making tabs height 0 when not active, breaks map
def inject_iframe_js_code(source: str) -> None:
    """
    Injects JavaScript code into a Streamlit app using an iframe.

    This function creates a hidden div with a unique ID and injects the provided
    JavaScript code into the parent document using an iframe. The iframe's source
    is a JavaScript URL that creates a script element, sets its type to 'text/javascript',
    and assigns the provided JavaScript code to its text content. The script element
    is then appended to the hidden div in the parent document.

    Args:
        source (str): The JavaScript code to be injected.

    Returns:
        None
    """
    div_id = uuid.uuid4()

    st.markdown(
        f"""
    <div style="height: 0; width: 0; overflow: hidden;" id="{div_id}">
        <iframe src="javascript: \
            var script = document.createElement('script'); \
            script.type = 'text/javascript'; \
            script.text = {html.escape(repr(source))}; \
            var div = window.parent.document.getElementById('{div_id}'); \
            div.appendChild(script); \
            setTimeout(function() {{ }}, 0); \
        "></iframe>
    </div>
    """,
        unsafe_allow_html=True,
    )
    
def js_show_zeroheight_iframe(component_iframe_title: str, height: str = "auto") -> None:
    """
    Injects JavaScript code to dynamically set iframe height (located by title)

    This function generates and injects JavaScript code that searches for
    iframes with the given title and sets their height to the specified value.
    The script attempts to find the iframes up to a maximum number of attempts,
    and also listens for user interactions to reattempt setting the height.
    
    See https://github.com/streamlit/streamlit/issues/7376 
    

    Args:
        component_iframe_title (str): The title attribute of the iframes to target.
        height (str, optional): The height to set for the iframes. Defaults to "auto".

    Notes:
        - The JavaScript code will attempt to find the iframes every 250
          milliseconds, up to a maximum of 20 attempts.
        - If the iframes are found, their height will be set to the specified value.
        - User interactions (e.g., click events) triggers a reattempt to set the height.
    """
    source = f"""
    (function() {{
    var attempts = 0;
    const maxAttempts = 20; // Max attempts to find the iframe
    const intervalMs = 250; // Interval between attempts in milliseconds

    function setIframeHeight() {{
        const intervalId = setInterval(function() {{
            var iframes = document.querySelectorAll('iframe[title="{component_iframe_title}"]');
            if (iframes.length > 0 || attempts > maxAttempts) {{
                if (iframes.length > 0) {{
                    iframes.forEach(iframe => {{
                        if (iframe || iframe.height === "0" || iframe.style.height === "0px") {{
                            iframe.style.height = "{height}";
                            iframe.setAttribute("height", "{height}");
                            console.log('Height of iframe with title "{component_iframe_title}" set to {height}.');
                        }}
                    }});
                }} else {{
                    console.log('Iframes with title "{component_iframe_title}" not found after ' + maxAttempts + ' attempts.');
                }}
                clearInterval(intervalId); // Stop checking
            }}
            attempts++;
        }}, intervalMs);
    }}


    function trackInteraction(event) {{
        console.log('User interaction detected:', event.type);
        setIframeHeight();
    }}

    setIframeHeight();
    document.addEventListener('click', trackInteraction);
}})();
    """
    inject_iframe_js_code(source)
