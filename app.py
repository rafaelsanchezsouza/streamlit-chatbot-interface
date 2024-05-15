import uuid
import random
from openai import AzureOpenAI
import streamlit as st
from dotenv import load_dotenv
import os
import shelve

load_dotenv()

st.title("Streamlit Chatbot Interface")

# Example lists of words to use for generating session names  
adjectives = ['Ancient', 'Mysterious', 'Silent', 'Eternal', 'Golden', 'Hidden', 'Forgotten', 'Lost', 'Majestic', 'Mythic']  
nouns = ['Forest', 'Ocean', 'Mountain', 'River', 'Sky', 'Flame', 'Star', 'Shadow', 'Light', 'Stone']  

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"
client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),  
    api_version="2024-02-01",
    azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    )

# Ensure openai_model is initialized in session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = os.getenv('AZURE_OPENAI_MODEL')

# Load chat history from shelve file for the current session  
def load_chat_history():  
    session_id = st.session_state.get("current_session_id", None)  
    if session_id:  
        with shelve.open("chat_history") as db:  
            return db.get(session_id, [])  
    return []  
  
def generate_session_name():  
    return random.choice(adjectives) + random.choice(nouns) + str(random.randint(100, 999))  

# Save chat history to shelve file for the current session  
def save_chat_history(messages):  
    session_id = st.session_state.get("current_session_id", None)  
    if session_id:  
        with shelve.open("chat_history") as db:  
            db[session_id] = messages  

# New chat session to shelve file
def new_chat_session():
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    session_name = generate_session_name()  # Assumes you have the generate_session_name function defined  
    print(f"New Chat Session: {session_name} (ID: {session_id})") 

    # Initialize an empty chat history for the new session in the shelve file
    with shelve.open("chat_history") as db:
        db[session_id] = []
        
    st.session_state["current_session_id"] = session_id  # Store the current session ID  
    
    print("New Chat")  

# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Lists all existing sessions
def get_all_session_ids():  
    with shelve.open("chat_history") as db:  
        return list(db.keys()) 

# Sidebar with a button to delete chat history
with st.sidebar:
    if st.button("New Chat"):
        st.session_state.messages = []
        new_chat_session()

    if st.button("Delete Chat History"):  
        # Ensure deletion only affects the current session's history  
        session_id = st.session_state.get("current_session_id", None)  
        if session_id:  
            with shelve.open("chat_history") as db:  
                del db[session_id]  # Delete the current session's chat history  
            st.session_state.messages = []  
        
    # Display a list of available sessions  
    session_ids = get_all_session_ids()  
    selected_session_id = st.selectbox("Available Sessions", session_ids, key="selected_session_id")  
    st.session_state["current_session_id"] = selected_session_id  
    st.session_state.messages = load_chat_history()  
  

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
            model=st.session_state["openai_model"],
            messages=st.session_state["messages"],
            stream=True,
        ):
            if response.choices:  
                full_response += response.choices[0].delta.content or ""  
            
            message_placeholder.markdown(full_response + "|")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Save chat history after each interaction
save_chat_history(st.session_state.messages)
