import os
import streamlit as st
from chatbot.factories import LLMFactory, DatabaseFactory, FileSystemFactory
from chatbot import utils
from config import environment
from components.styleguide_tab import render_styleguide_tab
from components.context_tab import render_context_tab

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

models = ["o4-mini", "gpt-4.1"]

def init_session_state(database_service):
    """Initialize and update Streamlit session state."""
    if "current_session_id" not in st.session_state:  
        st.session_state["current_session_id"] = database_service.new_chat_session()
    if "messages" not in st.session_state:
        st.session_state["messages"] = database_service.load_chat_history(st.session_state["current_session_id"])
    if 'append_file_structure' not in st.session_state:
        st.session_state['append_file_structure'] = False
    if 'list_modified_files' not in st.session_state:  
        st.session_state['list_modified_files'] = False  
    if 'list_all_files' not in st.session_state:  
        st.session_state['list_all_files'] = False  
    if 'project_context' not in st.session_state:
        st.session_state["project_context"] = ""
    if "folder_path" not in st.session_state:
        st.session_state["folder_path"] = ""

def show_sidebar(database_service):
    llm_service = get_llm_service()
    with st.sidebar:
        st.header("Chat")
        st.selectbox('Choose Model', models, index=0, key='selected_model')

        if st.button("New Chat"):
            new_session_id = database_service.new_chat_session()
            st.session_state["current_session_id"] = new_session_id
            st.session_state["messages"] = database_service.load_chat_history(new_session_id)  

        if st.button("Delete Chat History"):  
            database_service.delete_chat_history(st.session_state["current_session_id"]) 

        # Two columns for renaming chat
        rename1, rename2 = st.columns ([1,1])  
        with rename1:  
            chat_rename = st.text_input("Chat Name:")  
        with rename2:
            st.markdown("""<br>""", unsafe_allow_html=True)
            if st.button("Rename Chat"):
                old_session_id = st.session_state["current_session_id"]  
                new_session_id = chat_rename or utils.generate_smart_session_name(llm_service, st)
                new_session_id = database_service.change_session_id(old_session_id, new_session_id)  
                st.session_state["current_session_id"] = new_session_id 

        # Working folder selection
        folder_input, confirm_btn, msg_col = st.columns([2,1,1])
        with folder_input:
            folder_path = st.text_input("Working Folder:", value=st.session_state['folder_path'])
            st.session_state['folder_path'] = folder_path
        with confirm_btn:
            st.markdown("""<br>""", unsafe_allow_html=True)
            if st.button("Confirm"):  
                if os.path.isdir(folder_path):  
                    st.success("Folder found!")  
                    database_service.save_session_path(st.session_state["current_session_id"], folder_path)
                    st.session_state["folder_path"] = folder_path

                else:  
                    st.error("Not found.")

        # Project/file-related toggles
        st.session_state['append_file_structure'] = st.checkbox("Append File Structure")
        st.session_state['append_recent_files'] = st.checkbox("Append Recent Files")
        st.session_state['append_all_files'] = st.checkbox("Append All Files")
        st.session_state['append_styleguide'] = st.checkbox("Append Styleguide")

        # Session selection
        session_ids = database_service.get_all_session_ids()  
        current_id = st.session_state["current_session_id"]
        last_index = len(session_ids) - 1
        default_index = session_ids.index(current_id) if current_id in session_ids else last_index
        selected_session_id = st.selectbox("Available Sessions", session_ids, index=default_index, key="selected_session_id")
        if selected_session_id != st.session_state["current_session_id"]:
            st.session_state["current_session_id"] = selected_session_id
            st.session_state["messages"] = database_service.load_chat_history(selected_session_id)
            st.session_state["folder_path"] = database_service.load_session_path(selected_session_id)

def get_file_structure_context(folder_path, file_service):
    if os.path.isdir(folder_path):
        file_structure = file_service.get_all_files(folder_path)
        root = folder_path
    else:
        file_structure = file_service.get_all_files('.')
        root = '.'
    combined_files = f"Root Folder: {root} \n\nFile Structure:\n\n"
    for file in file_structure:
        combined_files += file + "\n\n"
    return combined_files

def get_recent_files_context(folder_path, file_service):
    if os.path.isdir(folder_path):
        files = file_service.get_files_modified_in_last_24_hours(folder_path)
    else:
        files = []
    combined = ""
    if files:
        for file in files:
            file_content = file_service.read_file_content(file)
            combined += f"Content of {file}:\n\n{file_content}\n\n\n----\n\n"
        return "Recent Files:\n\n" + combined
    return ""

def get_all_files_context(folder_path, file_service):
    if os.path.isdir(folder_path):
        files = file_service.get_all_files(folder_path)
    else:
        files = []
    combined = ""
    if files:
        for file in files:
            file_content = file_service.read_file_content(file)
            combined += f"Content of {file}:\n\n{file_content}\n\n\n----\n\n"
        return "Project Files:\n\n" + combined
    return ""

def get_styleguide(folder_path, file_service):
    if os.path.isdir(folder_path):
        files = file_service.get_all_files(folder_path)
    else:
        files = []
    combined = ""
    if files:
        for file in files:
            file_content = file_service.read_file_content(file)
            combined += f"Content of {file}:\n\n{file_content}\n\n\n----\n\n"
        return "Project Files:\n\n" + combined
    return ""

def display_chat(messages, database_service):
    """
    Show each message along with a small delete button.
    If delete is clicked, remove the message, persist, and rerun.
    """
    for idx, message in enumerate(messages):
        avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
        # each chat bubble can be treated as a little st.container
        with st.chat_message(message["role"], avatar=avatar):
            # two columns: one for the text, one for the delete button
            col_txt, col_del = st.columns([0.95, 0.05])
            with col_txt:
                st.markdown(message["content"])
            with col_del:
                btn_key = f"del_{st.session_state["current_session_id"]}_{idx}"
                if st.button("❌", key=btn_key, ):
                    # remove from session state
                    st.session_state["messages"].pop(idx)
                    # persist immediately
                    database_service.save_chat_history(
                        st.session_state["current_session_id"],
                        st.session_state["messages"]
                    )
                    # rerun so UI redraws without that message
                    st.rerun()

def get_llm_service():
    """Return a cached LLM service, re‑initializing only when
       st.session_state['selected_model'] changes."""
    selected = st.session_state.get("selected_model", models[0])
    # if we never made one, or the user just picked a new model:
    if (
       "llm_service" not in st.session_state
       or st.session_state.get("llm_model") != selected
    ):
        svc = LLMFactory.get_llm_service(selected)
        st.session_state["llm_service"] = svc
        st.session_state["llm_model"]   = selected
    return st.session_state["llm_service"]

def main():
        # Inject CSS to shrink buttons globally (you can scope it if you like)
    st.markdown(
        """
        <style>
        /* Only style buttons inside a container whose class includes "st-key-del_" */
        div.stElementContainer[class*="st-key-del_"] button {
            padding: 0px !important;
            border: none;
            font-size: 0rem !important;
            line-height: 0.5px !important;
            background: transparent !important;
            color: #ce885f !important;        
        }
        /* Optional—lighter hover effect */
        div.stElementContainer[class*="st-key-del_"] button:hover {
            background: rgba(224,0,0,0.1) !important;
        }
        </style>
        """,
    unsafe_allow_html=True,
    )
    
    tab_chat, tab_style, tab_context = st.tabs(["Chat", "Style Guide", "Context"])

    database_service = DatabaseFactory.get_database_service(environment.settings.DATABASE_TYPE)
    file_service = FileSystemFactory.get_file_system("local")
    # You could persist LLM service or allow switching, depending on your needs.
    llm_service = get_llm_service()
    init_session_state(database_service)

    # --- Sidebar ---
    show_sidebar(database_service)
    

    # --- Project Context ---
    folder_path = st.session_state.get('folder_path', '')
    st.session_state["project_context"] = get_all_files_context(folder_path, file_service)
    st.session_state["styleguide"] = file_service.read_file_content("./styleguide.json")

    with tab_chat:
        # --- Chat window & Input ---
        display_chat(st.session_state["messages"], database_service)

    prompt = st.chat_input("How can I help?")
    if prompt:
        # Build project context based on current checkbox states
        project_context = []
        if st.session_state.get('append_file_structure', False):
            file_structure = get_file_structure_context(folder_path, file_service)
            project_context.append(file_structure)
        
        if st.session_state.get('append_recent_files', False):
            recent_files = get_recent_files_context(folder_path, file_service)
            project_context.append(recent_files)
        
        if st.session_state.get('append_all_files', False):
            project_context.append(st.session_state["project_context"])
        
        if st.session_state.get('append_styleguide', False):
            project_context.append(st.session_state["styleguide"])
        
        # Combine all context sections
        combined_context = "\n\n".join(project_context)
        chat_input = prompt + "\n\n" + combined_context if combined_context else prompt
        
        st.session_state["messages"].append({"role": "user", "content": chat_input})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(chat_input)
        with st.chat_message("assistant", avatar=BOT_AVATAR):
            message_placeholder = st.empty()
            full_response = ""
            for response in llm_service.query(st.session_state["messages"]):
                if response.choices:  
                    full_response += response.choices[0].delta.content or ""  
                message_placeholder.markdown(full_response + "|")
            message_placeholder.markdown(full_response)
        st.session_state["messages"].append({"role": "assistant", "content": full_response})

        # Save at end
        database_service.save_chat_history(st.session_state["current_session_id"], st.session_state["messages"])

    with tab_style:
        render_styleguide_tab()
    
    with tab_context:
        render_context_tab()

if __name__ == "__main__":
    main()