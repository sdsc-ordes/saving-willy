import streamlit as st

def refresh_progress():
    with st.sidebar:
        tot = st.session_state.workflow_fsm.num_states - 1
        cur_i = st.session_state.workflow_fsm.current_state_index
        cur_t = st.session_state.workflow_fsm.current_state
        st.session_state.disp_progress[0].markdown(f"*Progress: {cur_i}/{tot}. Current: {cur_t}.*")
        st.session_state.disp_progress[1].progress(cur_i/tot)
    
def init_workflow_viz():
    # add progress indicator to session_state
    if "progress" not in st.session_state:
        with st.sidebar:
            st.session_state.disp_progress = [st.empty(), st.empty()]
            # add button to sidebar, with the callback to refesh_progress
            st.sidebar.button("Refresh Progress", on_click=refresh_progress)

