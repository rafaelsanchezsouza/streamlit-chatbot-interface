import os, json
from pathlib import Path
import streamlit as st
from chatbot.services.commit_service import GitCommitManager

def render_commit_tab():
    st.header("commit editor")

    folder_path = st.session_state.get('folder_path', '')
    manager = GitCommitManager(repo_path=folder_path)

    # Get working folder from session state
    folder_path = st.session_state.get('folder_path', '')
    if not folder_path or not os.path.isdir(folder_path):
        st.error("Please select a valid working folder in the sidebar.")
        return

    # Add auto-update button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 Generate"):
            try:
                # Generate new rules from diffs
                new_commit = manager.generate_new_commit()
                
                # Update text area
                st.session_state["commit_text"] = new_commit
                
            except Exception as e:
                st.error(f"Auto commit failed: {str(e)}")
                
    if "commit_text" not in st.session_state:
        st.session_state["commit_text"] = []

    st.session_state["commit_text"] = st.text_area(
        "Edit your commit below:",
        value=st.session_state["commit_text"],
        height=400,
        key="commit_text_area",
    )

    if st.button("💾 Commit Code"):
        try:
            # parsed = json.loads(st.session_s;state["commit_text"])
            # styleguide_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")
            st.success("Changes commited!")
        except json.JSONDecodeError as err:
            st.error(f"Invalid JSON: {err}")