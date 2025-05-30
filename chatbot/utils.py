import random  
import os
  
# Example lists of words to use for generating session names  
adjectives = ['Ancient', 'Mysterious', 'Silent', 'Eternal', 'Golden', 'Hidden', 'Forgotten', 'Lost', 'Majestic', 'Mythic']  
nouns = ['Forest', 'Ocean', 'Mountain', 'River', 'Sky', 'Flame', 'Star', 'Shadow', 'Light', 'Stone']  
  
def generate_session_name():  
    return random.choice(adjectives) + random.choice(nouns) + str(random.randint(100, 999))  

def generate_smart_session_name(llm_service, st):  
    prompt = "provide me a name that describes our chat session, without spaces, you can use hyphen. don't answer anything else but the name"
    temp = st
    temp.session_state.messages.append({"role": "user", "content": prompt})  

    # Assuming 'client.chat.completions.create()' sends the question and gets a response  
    full_response = ""
    llm_model = "gpt-4-turbo-0125-preview"
    for response in llm_service.query(temp.session_state.messages): 
      if response.choices:
          full_response += response.choices[0].delta.content or ""
      
    return full_response
    
def get_file_structure(root_dir):
    file_structure = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        relative_path = os.path.relpath(dirpath, root_dir)
        file_structure[relative_path] = {
            'directories': dirnames,
            'files': filenames
        }
    return file_structure