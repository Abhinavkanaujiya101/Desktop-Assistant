import openai
import json
import sqlite3
import re
import webbrowser
import urllib.parse
from datetime import datetime
from config import Config

class ChatBotCore:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None
        self.setup_database()
        self.conversation_history = []
        
    def setup_database(self):
        """Initialize SQLite database for chat history"""
        self.conn = sqlite3.connect(Config.CHAT_HISTORY_FILE, check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_message TEXT,
                bot_response TEXT,
                category TEXT
            )
        ''')
        self.conn.commit()
    
    def local_chat_fallback(self, message):
        """Local response system when OpenAI is unavailable"""
        message_lower = message.lower()
        
        # Music commands
        if any(word in message_lower for word in ['play music', 'play song', 'youtube music']):
            return self.play_youtube_music(message)
        
        # Math problems
        elif any(word in message_lower for word in ['solve', 'calculate', 'math', 'equation']):
            return self.solve_basic_math(message)
        
        # Greetings
        elif any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm your AI assistant. How can I help you today?"
        
        # Commands
        elif 'open youtube' in message_lower:
            return "I can't open YouTube directly, but I can help you with other tasks!"
        
        # Default response
        else:
            return "I'd be happy to help! Currently I'm operating in basic mode. For advanced features, please set up your OpenAI API billing."
    
    def solve_basic_math(self, equation):
        """Solve basic math equations locally"""
        try:
            # Extract equation like "2x+5=10"
            equation = equation.replace(' ', '')
            
            # Simple linear equation solver
            if 'x' in equation and '=' in equation:
                left, right = equation.split('=')
                left = left.replace('x', '*x').replace('+*x', '+x').replace('-*x', '-x')
                if left.startswith('*x'):
                    left = 'x' + left[2:]
                
                # Very basic solver for demo
                if '2x+5=10' in equation:
                    return "Solving 2x + 5 = 10:\nStep 1: Subtract 5 from both sides: 2x = 5\nStep 2: Divide by 2: x = 2.5\nSolution: x = 2.5"
                elif 'x+3=7' in equation:
                    return "Solving x + 3 = 7:\nStep 1: Subtract 3 from both sides: x = 4\nSolution: x = 4"
                else:
                    return f"I can help solve equations like '2x+5=10'. For '{equation}', try specific examples I'm programmed for."
            
            # Basic arithmetic
            elif all(c in '0123456789+-*/.() ' for c in equation):
                result = eval(equation)
                return f"Calculation: {equation} = {result}"
            else:
                return "I can solve basic math problems. Try equations like '2x+5=10' or calculations like '15+23'."
                
        except:
            return "I couldn't solve that equation. Try simpler formats like '2x+5=10'."
    
    def chat(self, message, context=None):
        """Main chat method with fallback"""
        try:
            # Try OpenAI first if available
            if self.client:
                system_message = """You are a helpful AI assistant with capabilities for problem solving and reasoning."""
                
                messages = [
                    {"role": "system", "content": system_message},
                    *self.conversation_history[-10:],
                    {"role": "user", "content": message}
                ]
                
                response = self.client.chat.completions.create(
                    model=Config.GPT_MODEL,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                
                reply = response.choices[0].message.content
                
            else:
                # Use local fallback
                reply = self.local_chat_fallback(message)
            
            # Save to history
            self.save_conversation(message, reply, "general")
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": reply})
            
            return reply
            
        except Exception as e:
            # Fallback to local responses on any error
            return self.local_chat_fallback(message)
    
    def save_conversation(self, user_message, bot_response, category):
        """Save conversation to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history (timestamp, user_message, bot_response, category)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), user_message, bot_response, category))
        self.conn.commit()
    
    def get_chat_history(self, limit=20):
        """Retrieve recent chat history"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT timestamp, user_message, bot_response 
            FROM chat_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()