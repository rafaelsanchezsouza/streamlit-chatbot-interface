import os
import streamlit as st
from chatbot.factories import LLMFactory, DatabaseFactory, FileSystemFactory
from chatbot import utils
from config import environment

st.title("Streamlit Chatbot Interface")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# Initialize AzureOpenAI client  
llm_service = LLMFactory.get_llm_service(environment.settings.LLM_API_TYPE)
database_service = DatabaseFactory.get_database_service(environment.settings.DATABASE_TYPE)
file_service = FileSystemFactory.get_file_system("local")

# Ensure openai_model is initialized in session state
if "current_session_id" not in st.session_state:  
    # Generate a new session  
    st.session_state["current_session_id"] = database_service.new_chat_session()  
  
# Load chat history from the current session  
st.session_state.messages = database_service.load_chat_history(st.session_state["current_session_id"]) 

# Initializes Append File Structure
if 'append_file_structure' not in st.session_state:
    st.session_state['append_file_structure'] = False

if 'list_modified_files' not in st.session_state:  
    st.session_state['list_modified_files'] = False  
  
if 'list_all_files' not in st.session_state:  
    st.session_state['list_all_files'] = False  

st.session_state["project_context"] = ""


# Sidebar with Options
with st.sidebar:
    if st.button("New Chat"):
        st.session_state["current_session_id"] = st.session_state.messages = []
        new_session_id = database_service.new_chat_session()
        st.session_state["current_session_id"] = new_session_id
        st.session_state.messages = database_service.load_chat_history(new_session_id)  

    if st.button("Rename Chat"):
        # Generate a new unique session ID  
        new_session_id = utils.generate_smart_session_name(llm_service, st);  
        old_session_id = st.session_state["current_session_id"]  
        new_session_id = database_service.change_session_id(old_session_id, new_session_id)  
        st.session_state["current_session_id"] = new_session_id 

    if st.button("Delete Chat History"):  
        # Ensure deletion only affects the current session's history  
        database_service.delete_chat_history(st.session_state["current_session_id"]) 

    if st.checkbox("Append File Structure"):
        file_structure = file_service.read_directory_structure('.')
        st.session_state["project_context"] = "File Structure:" + "\n\n" + file_structure
        st.session_state['append_file_structure'] = True

    if st.checkbox("Append Recent Files"):
        files = file_service.get_files_modified_in_last_24_hours('.') 
        combined_file_contents = ""  # Initialize an empty string to accumulate file contents 
        
        if files:  
            for file in files:  
                file_content = file_service.read_file_content(file)  
                # Append this file's content to the combined string, add a delimiter for readability
                combined_file_contents += f"Content of {file}:\n```\n{file_content}\n```\n\n----\n\n"

                st.session_state["project_context"] = "Recent Files:" + "\n\n" + combined_file_contents
        else:  
            st.write("No files changed in the last 24 hours.")  

    if st.checkbox("Append All Files"):
        files = file_service.get_all_files('.')  
        combined_file_contents = ""  # Initialize an empty string to accumulate file contents

        if files:
            for file in files:
                file_content = file_service.read_file_content(file)
                # Append this file's content to the combined string, add a delimiter for readability
                combined_file_contents += f"Content of {file}:\n```\n{file_content}\n```\n\n----\n\n"

                st.session_state["project_context"] = "Project Files:" + "\n\n" + combined_file_contents

            else:  
                st.write("No files found.")  
        
    # Display a list of available sessions  
    session_ids = database_service.get_all_session_ids()  
    new_session_id = st.session_state["current_session_id"]

    last_index = len(session_ids) - 1  

    default_index = session_ids.index(new_session_id) if new_session_id in session_ids else last_index

    selected_session_id = st.selectbox("Available Sessions", session_ids, index=default_index, key="selected_session_id") 

    st.session_state["current_session_id"] = selected_session_id  
    st.session_state.messages = database_service.load_chat_history(selected_session_id)    

# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Main chat interface
if prompt := st.chat_input("How can I help?"):
    
    # includes file struture in prompt
    prompt = prompt + "\n\n" + st.session_state["project_context"]

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        full_response = ""
        for response in llm_service.query(st.session_state.messages):
            if response.choices:  
                full_response += response.choices[0].delta.content or ""  
            
            message_placeholder.markdown(full_response + "|")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Save chat history after each interaction
database_service.save_chat_history(st.session_state["current_session_id"], st.session_state.messages)  
