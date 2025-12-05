import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys (set these in your .env file)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    WOLFRAM_ALPHA_APP_ID = os.getenv('WOLFRAM_ALPHA_APP_ID')
    
    # Model Configuration
    GPT_MODEL = "gpt-3.5-turbo"
    
    # File Paths
    CHAT_HISTORY_FILE = "chat_history.json"
    TASKS_DB = "tasks.db"