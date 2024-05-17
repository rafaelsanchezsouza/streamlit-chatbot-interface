import streamlit as st
from openai import AzureOpenAI
from chatbot import models, utils 
from config import settings  

st.title("Streamlit Chatbot Interface")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# Initialize AzureOpenAI client  
client = AzureOpenAI(  
    api_key=settings.AZURE_OPENAI_API_KEY,  
    api_version="2024-02-01",  
    azure_endpoint=settings.AZURE_OPENAI_ENDPOINT  
)  

# Ensure openai_model is initialized in session state
if "current_session_id" not in st.session_state:  
    # Generate a new session  
    st.session_state["current_session_id"] = models.new_chat_session()  
  
# Load chat history from the current session  
st.session_state.messages = models.load_chat_history(st.session_state["current_session_id"]) 

# Sidebar with a button to delete chat history
with st.sidebar:
    if st.button("New Chat"):
        st.session_state["current_session_id"] = st.session_state.messages = []
        new_session_id = models.new_chat_session()
        st.session_state["current_session_id"] = new_session_id
        st.session_state.messages = models.load_chat_history(new_session_id)  

    if st.button("Rename Chat"):
        old_session_id = st.session_state["current_session_id"]  
        new_session_id = models.change_session_id(old_session_id, client, st, settings)  
        st.session_state["current_session_id"] = new_session_id 

    if st.button("Delete Chat History"):  
        # Ensure deletion only affects the current session's history  
        models.delete_chat_history(st.session_state["current_session_id"]) 
        
    # Display a list of available sessions  
    session_ids = models.get_all_session_ids()  
    new_session_id = st.session_state["current_session_id"]

    default_index = session_ids.index(new_session_id) if new_session_id in session_ids else 0

    selected_session_id = st.selectbox("Available Sessions", session_ids, index=default_index, key="selected_session_id") 

    st.session_state["current_session_id"] = selected_session_id  
    st.session_state.messages = models.load_chat_history(selected_session_id)    

# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Main chat interface
if prompt := st.chat_input("How can I help?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=st.session_state.get("openai_model", settings.AZURE_OPENAI_MODEL),
            messages=st.session_state["messages"],
            stream=True,
        ):
            if response.choices:  
                full_response += response.choices[0].delta.content or ""  
            
            message_placeholder.markdown(full_response + "|")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Save chat history after each interaction
models.save_chat_history(st.session_state["current_session_id"], st.session_state.messages)  
