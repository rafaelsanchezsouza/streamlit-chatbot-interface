import os
import json
from pathlib import Path
import streamlit as st
from chatbot.services.commit_service import GitCommitManager

def render_commit_tab():
    st.header("Commit Editor")

    # Get default folder path from session state
    default_folder_path = st.session_state.get('folder_path', '')
    
    # Allow user to specify Git repository path
    git_folder_path = st.text_input(
        "Git Repository Path",
        value=default_folder_path,
        key="git_repo_path_input",
        help="Path to Git repository (might differ from working folder)"
    )

    # Validate Git repository path
    try:
        manager = GitCommitManager(repo_path=git_folder_path)
    except Exception as e:
        st.error(f"Invalid Git repository: {str(e)}")
        return

    make_pt = st.checkbox("In portuguese", value=True)

    # Auto-generate commit section
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 Generate"):
            try:
                new_commit, diffs = manager.generate_new_commit(in_portuguese=make_pt)
                st.session_state["commit_text"] = new_commit
                st.session_state["diffs"] = diffs
                st.rerun()
            except Exception as e:
                st.error(f"Commit generation failed: {str(e)}")

    # Commit message editor
    commit_message = st.text_area(
        "Commit Message:",
        value=st.session_state.get("commit_text", ""),
        height=300,
        key="commit_editor"
    )

    if st.button("🟩🟥 Get Diff"):
        try:
            diffs = manager._get_staged_diffs()
            st.session_state["diffs"] = diffs
            st.rerun()
        except Exception as e:
            st.error(f"Diff get failed: {str(e)}")
    
    # Diff editor
    st.text_area(
        "Diffs:",
        value=st.session_state.get("diffs", ""),
        height=300,
        key="diff_viewer"
    )

    # Commit action section
    if st.button("💾 Commit Changes", type="primary"):
        try:
            if not commit_message.strip():
                raise ValueError("Commit message cannot be empty")
            
            # manager.commit_changes(commit_message)
            st.success("Successfully committed changes!")
            # st.session_state["commit_text"] = ""  # Clear commit message
        except Exception as e:
            st.error(f"Commit failed: {str(e)}")

    # # Display recent commit history
    # st.subheader("Recent Commit History")
    # try:
    #     commit_history = manager.get_commit_history(limit=5)
    #     for commit in commit_history:
    #         st.markdown(f"**{commit['hash']}**: {commit['message']}")
    # except Exception as e:
    #     st.error(f"Failed to load commit history: {str(e)}")