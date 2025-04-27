# components/styleguide_tab.py
import os, json
from pathlib import Path
import streamlit as st
from chatbot.services.styleguide_service import GitStyleGuideManager

def render_styleguide_tab():
    st.header("styleguide.json editor")

    # Get working folder from session state
    folder_path = st.session_state.get('folder_path', '')
    if not folder_path or not os.path.isdir(folder_path):
        st.error("Please select a valid working folder in the sidebar.")
        return

    # Initialize styleguide manager
    styleguide_path = Path(folder_path) / "styleguide.json"
    try:
        manager = GitStyleGuideManager(repo_path=folder_path, styleguide_path=styleguide_path)
    except Exception as e:
        st.error(f"Failed to initialize Git repository: {str(e)}")
        return

    # Add auto-update button
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🔄 Auto-Update from Git Diffs"):
            try:
                result = manager.update_styleguide()
                st.success(f"Added {result['added']} new rules from staged changes!")
                st.rerun()
            except Exception as e:
                st.error(f"Update failed: {str(e)}")

    # Existing editor functionality
    try:
        raw = styleguide_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as e:
        data = {}
        raw = json.dumps(data, indent=2)
        st.error(f"Could not parse JSON: {e}")

    if "styleguide_text" not in st.session_state:
        st.session_state["styleguide_text"] = raw

    st.session_state["styleguide_text"] = st.text_area(
        "Edit your styleguide.json below:",
        value=st.session_state["styleguide_text"],
        height=400,
        key="styleguide_text_area",
    )

    if st.button("💾 Save styleguide.json"):
        try:
            parsed = json.loads(st.session_state["styleguide_text"])
            styleguide_path.write_text(json.dumps(parsed, indent=2), encoding="utf-8")
            st.success("styleguide.json saved!")
        except json.JSONDecodeError as err:
            st.error(f"Invalid JSON: {err}")