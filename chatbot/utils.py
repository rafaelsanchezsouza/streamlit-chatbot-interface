import random  
  
# Example lists of words to use for generating session names  
adjectives = ['Ancient', 'Mysterious', 'Silent', 'Eternal', 'Golden', 'Hidden', 'Forgotten', 'Lost', 'Majestic', 'Mythic']  
nouns = ['Forest', 'Ocean', 'Mountain', 'River', 'Sky', 'Flame', 'Star', 'Shadow', 'Light', 'Stone']  
  
def generate_session_name():  
    return random.choice(adjectives) + random.choice(nouns) + str(random.randint(100, 999))  