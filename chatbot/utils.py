import random  
  
# Example lists of words to use for generating session names  
adjectives = ['Ancient', 'Mysterious', 'Silent', 'Eternal', 'Golden', 'Hidden', 'Forgotten', 'Lost', 'Majestic', 'Mythic']  
nouns = ['Forest', 'Ocean', 'Mountain', 'River', 'Sky', 'Flame', 'Star', 'Shadow', 'Light', 'Stone']  
  
def generate_session_name():  
    return random.choice(adjectives) + random.choice(nouns) + str(random.randint(100, 999))  

def generate_smart_session_name(client, st, settings):  
    prompt = "provide me a name that describes our chat session, without spaces, you can use hyphen. don't answer anything else but the name"
    temp = st
    temp.session_state.messages.append({"role": "user", "content": prompt})  

    # Assuming 'client.chat.completions.create()' sends the question and gets a response  
    chat_response = client.chat.completions.create(  
        model=st.session_state.get("openai_model", settings.AZURE_OPENAI_MODEL),  
        messages=temp.session_state["messages"],
    )  
      
    # Assuming the response structure allows accessing the text directly,  
    # we store the first response in a variable without adding it to the session or displaying it  
    if chat_response.choices and chat_response.choices[0].message:  
        bot_response = chat_response.choices[0].message.content  
    else:  
        bot_response = generate_session_name()
      
    return bot_response
    