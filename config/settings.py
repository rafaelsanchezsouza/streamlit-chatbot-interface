from dotenv import load_dotenv  
import os  
  
load_dotenv()  
  
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')  
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')  
AZURE_OPENAI_MODEL = os.getenv('AZURE_OPENAI_MODEL')  