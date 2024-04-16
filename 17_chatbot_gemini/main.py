from ai import LLM
from datasets import load_dataset
    
api_key = '' # Add your Google API key here
dataset = load_dataset("MuskumPillerum/General-Knowledge") # Add the dataset of your choice

if not api_key:
    with open('17_chatbot_gemini/config.ini') as f:
        api_key = f.read()

llm = LLM(api_key)

