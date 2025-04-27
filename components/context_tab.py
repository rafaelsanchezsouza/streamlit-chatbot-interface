# components/context_tab.py
import streamlit as st

def render_context_tab():
    st.header("Context Viewer")
    
    # Retrieve project context from session state, default to placeholder if not set
    project_context = st.session_state.get("project_context", "No project context available. Please confirm a valid working folder.")

    # Display the context in a read-only text area
    st.text_area(
        "Project Context",
        value=project_context,
        height=600,
        key="project_context_viewer"
    )