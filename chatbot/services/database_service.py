import shelve
from datetime import datetime
from chatbot.interfaces import DatabaseService

class ShelveDatabaseService(DatabaseService):
    def _load_raw(self, session_id):
        with shelve.open("chat_history") as db:
            entry = db.get(session_id, [])
        if isinstance(entry, list):
            return {"messages": entry, "path": ""}
        else:
            return entry  # assume already a dict

    def load_chat_history(self, session_id):
        return self._load_raw(session_id)["messages"]

    def load_session_path(self, session_id):
        return self._load_raw(session_id).get("path", "")

    def save_chat_history(self, session_id, messages):
        # pull in the old path, in case it’s already been set
        old = self._load_raw(session_id)
        new = {"messages": messages, "path": old.get("path","")}
        with shelve.open("chat_history") as db:
            db[session_id] = new

    def save_session_path(self, session_id, path):
        old = self._load_raw(session_id)
        new = {"messages": old.get("messages",[]), "path": path}
        with shelve.open("chat_history") as db:
            db[session_id] = new

    def new_chat_session(self):
        # e.g. "20240625T143055123456"
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        session_id = timestamp

        with shelve.open("chat_history") as db:
            db[session_id] = []   # initialize an empty history list

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
