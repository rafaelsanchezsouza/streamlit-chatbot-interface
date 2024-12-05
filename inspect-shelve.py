# import shelve  
  
# def view_chat_sessions():  
#     with shelve.open("chat_history") as db:  
#         for session_id in db.keys():  
#             print(f"Session ID: {session_id}")  
#             for message in db[session_id]:  
#                 print(message)  
  
# if __name__ == "__main__":  
#     view_chat_sessions()  

import shelve  
import json  
  
def export_sessions_to_json(filepath="chat_sessions.json"):  
    with shelve.open("chat_history") as db:  
        all_sessions = {session_id: db[session_id] for session_id in db.keys()}  
      
    with open(filepath, "w") as json_file:  
        json.dump(all_sessions, json_file, indent=4)  
  
if __name__ == "__main__":  
    export_sessions_to_json()  
