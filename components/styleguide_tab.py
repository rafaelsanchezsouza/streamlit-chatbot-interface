# components/styleguide_tab.py
import os, json
from pathlib import Path
import streamlit as st

def render_styleguide_tab():
    st.header("styleguide.json editor")

    # decide where to read/write
    root    = Path(os.getcwd())
    sg_file = root / "styleguide.json"

    # if missing, initialize it
    if not sg_file.exists():
        sg_file.write_text(json.dumps({}, indent=2), encoding="utf-8")
        st.info("Created new styleguide.json")

    # load (or fallback if corrupted)
    try:
        raw  = sg_file.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as e:
        data = {}
        raw  = json.dumps(data, indent=2)
        st.error(f"Could not parse JSON: {e}")

    # keep edits in session_state
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
            sg_file.write_text(json.dumps(parsed, indent=2), encoding="utf-8")
            st.success("styleguide.json saved!")
        except json.JSONDecodeError as err:
            st.error(f"Invalid JSON, fix before saving: {err}")