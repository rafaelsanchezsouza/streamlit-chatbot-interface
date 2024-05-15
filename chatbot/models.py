import shelve  
import uuid  
  
# Load chat history from shelve file for the current session  
def load_chat_history(session_id):  
    if session_id:  
        with shelve.open("chat_history") as db:  
            return db.get(session_id, [])  
    return []  

# Save chat history to shelve file for the current session  
def save_chat_history(session_id, messages):  
    if session_id:  
        with shelve.open("chat_history") as db:  
            db[session_id] = messages  

# New chat session to shelve file
def new_chat_session():
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    print(f"New Chat Session: {session_id})") 

    # Initialize an empty chat history for the new session in the shelve file
    with shelve.open("chat_history") as db:
        db[session_id] = []
        
    return session_id

def delete_chat_history(session_id):  
    with shelve.open("chat_history") as db:  
        del db[session_id]  

# Lists all existing sessions
def get_all_session_ids():  
    with shelve.open("chat_history") as db:  
        return list(db.keys()) 