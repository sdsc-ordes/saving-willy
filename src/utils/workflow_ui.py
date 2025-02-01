import streamlit as st

def refresh_progress_display() -> None:
    """
    Updates the workflow progress display in the Streamlit sidebar.
    """
    with st.sidebar:
        num_states = st.session_state.workflow_fsm.num_states - 1
        current_state_index = st.session_state.workflow_fsm.current_state_index
        current_state_name = st.session_state.workflow_fsm.current_state
        colour = 'primary' 
        if current_state_index == num_states: # highlight that we finished
            colour = 'green'
        status = f":{colour}[*Progress: {current_state_index}/{num_states}. Current: {current_state_name}.*]"
        
        st.session_state.disp_progress[0].markdown(status)
        st.session_state.disp_progress[1].progress(current_state_index/num_states)

    
def init_workflow_viz(debug:bool=True) -> None:
    """
    Set up the streamlit elements for visualising the workflow progress.

    Adds placeholders for progress indicators, and adds a button to manually refresh
    the displayed progress. Note: The button is mainly a development aid.

    Args:
        debug (bool): If True, include the manual refresh button. Default is True.
        
    """

    
    #Initialise the layout containers used in the input handling
    # add progress indicator to session_state
    if "progress" not in st.session_state:
        with st.sidebar:
            st.session_state.disp_progress = [st.empty(), st.empty()]
            if debug:
                # add button to sidebar, with the callback to refesh_progress
                st.sidebar.button("Refresh Progress", on_click=refresh_progress_display)

