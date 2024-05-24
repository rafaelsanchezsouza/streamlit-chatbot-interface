import shelve
import uuid
from chatbot.interfaces import DatabaseService

class ShelveDatabaseService(DatabaseService):
    def load_chat_history(self, session_id):
        if session_id:  
            with shelve.open("chat_history") as db:  
                return db.get(session_id, [])  
        return []  

    def save_chat_history(self, session_id, messages):
        if session_id:  
            with shelve.open("chat_history") as db:  
                db[session_id] = messages  

    def new_chat_session(self):
        session_id = str(uuid.uuid4())
        with shelve.open("chat_history") as db:
            db[session_id] = []
        return session_id

    def delete_chat_history(self, session_id):
        with shelve.open("chat_history") as db:
            del db[session_id]

    def get_all_session_ids(self):
        with shelve.open("chat_history") as db:
            return list(db.keys())
        
    def change_session_id(self, old_session_id, new_session_id):  
        with shelve.open("chat_history") as db:  
            # Ensure the old session exists  
            if old_session_id in db:  
                # Copy the data to a new session ID  
                db[new_session_id] = db[old_session_id]  
                # Delete the old session  
                del db[old_session_id]  
            else:  
                print("Session not found.")  
        
        return new_session_id
