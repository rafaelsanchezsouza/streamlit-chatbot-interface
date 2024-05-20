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
        st.session_state["file_structure"] = file_service.read_directory_structure('.')
        st.session_state['append_file_structure'] = True
        # st.json(file_structure) # DEBUG only
    else: 
        st.session_state["file_structure"] = ""

    if st.button("Files Modified in Last 24 Hours"):
        changed_files = file_service.get_files_modified_in_last_24_hours('.')
        if changed_files:
            st.write("Files changed in the last 24 hours:")
            for file in changed_files:
                st.write(f"{file}")
                # Read and display the content of the file  
                file_content = file_service.read_file_content(file)  
                st.text_area("", value=file_content, height=200)  
        else:
            st.write("No files changed in the last 24 hours.")

    if st.button("List All Files"):  
        all_files = file_service.get_all_files('.')  
        if all_files:  
            st.write("All files (excluding .gitignore rules):")  
            for file in all_files:  
                st.write(file)  
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
    prompt = prompt + "\n\n" + st.session_state["file_structure"]

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
