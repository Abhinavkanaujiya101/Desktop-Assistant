import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
import os
import platform
import subprocess
import webbrowser
import urllib.parse
from chatbot_core import ChatBotCore
from reasoning_engine import ReasoningEngine
from task_manager import TaskManager
from utilities import Utilities

class ChatBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Desktop ChatBot")
        self.root.geometry("800x600")
        
        # Initialize components
        self.chatbot = ChatBotCore()
        self.reasoning_engine = ReasoningEngine()
        self.task_manager = TaskManager()
        self.utilities = Utilities()
        
        # Platform detection
        self.system = platform.system().lower()
        
        self.setup_gui()
    
    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            main_frame, 
            wrap=tk.WORD, 
            width=80, 
            height=25,
            state=tk.DISABLED
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X)
        
        self.user_input = ttk.Entry(input_frame, font=('Arial', 12))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind('<Return>', lambda e: self.send_message())
        
        # Buttons
        send_btn = ttk.Button(input_frame, text="Send", command=self.send_message)
        send_btn.pack(side=tk.RIGHT)
        
        # Features frame
        features_frame = ttk.Frame(main_frame)
        features_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(features_frame, text="Voice Input", 
                  command=self.voice_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(features_frame, text="Solve Math", 
                  command=self.math_solver).pack(side=tk.LEFT, padx=5)
        ttk.Button(features_frame, text="Add Task", 
                  command=self.add_task_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(features_frame, text="Screenshot", 
                  command=self.take_screenshot).pack(side=tk.LEFT, padx=5)
        ttk.Button(features_frame, text="Play Music", 
                  command=self.play_music_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(features_frame, text="Open App", 
                  command=self.open_app_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(features_frame, text="Clear Chat", 
                  command=self.clear_chat).pack(side=tk.LEFT, padx=5)
        
        # Welcome message
        self.display_message("Bot", "Hello! I'm your AI assistant. How can I help you today?")
    
    def display_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self):
        message = self.user_input.get().strip()
        if not message:
            return
        
        self.user_input.delete(0, tk.END)
        self.display_message("You", message)
        
        # Process in thread to prevent GUI freezing
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()
    
    def process_message(self, message):
        response = self.route_message(message)
        self.root.after(0, lambda: self.display_message("Bot", response))
    
    def play_youtube_music(self, message):
        """Play music on YouTube based on user request"""
        try:
            # Extract song name from different command patterns
            song_query = message.lower()
            
            # Remove command words
            remove_words = ['play', 'music', 'song', 'on', 'youtube', 'please', 'could you', 'can you']
            for word in remove_words:
                song_query = song_query.replace(word, '')
            
            song_query = song_query.strip()
            
            # If no specific song mentioned, play trending music
            if not song_query or song_query in ['', 'music', 'some music']:
                url = "https://www.youtube.com/watch?v=aqz-KE-bpKQ"  # YouTube Music trending
                webbrowser.open(url)
                return "🎵 Playing trending music on YouTube!"
            
            # Search for the specific song
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(song_query)}"
            webbrowser.open(search_url)
            return f"🎵 Searching YouTube for: {song_query}"
            
        except Exception as e:
            return f"Error playing music: {str(e)}"
    
    def play_music_dialog(self):
        """Dialog for playing music"""
        song_name = simpledialog.askstring("Play Music", "Enter song name or type 'music' for trending:")
        if song_name:
            if song_name.lower() in ['', 'music', 'trending']:
                result = self.play_youtube_music("play music")
            else:
                result = self.play_youtube_music(f"play {song_name}")
            self.display_message("Bot", result)
    
    def open_local_application(self, app_name):
        """Open local applications based on the operating system"""
        app_name_lower = app_name.lower()
        
        # Common applications mapping
        app_commands = {
            # Windows applications
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'file explorer': 'explorer.exe',
            'command prompt': 'cmd.exe',
            'powershell': 'powershell.exe',
            'task manager': 'taskmgr.exe',
            'control panel': 'control.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'powerpoint': 'powerpnt.exe',
            
            # Cross-platform applications (handled separately)
            'chrome': 'chrome',
            'firefox': 'firefox',
            'edge': 'msedge',
            'vscode': 'code',
            'visual studio code': 'code',
            'spotify': 'spotify',
            'discord': 'discord',
            'whatsapp': 'whatsapp',
            
            # macOS applications
            'textedit': 'TextEdit',
            'preview': 'Preview',
            'finder': 'Finder',
            'safari': 'Safari',
            
            # Linux applications
            'gedit': 'gedit',
            'nautilus': 'nautilus',
            'terminal': 'gnome-terminal',
            'libreoffice': 'libreoffice',
        }
        
        # Special cases that need different handling
        special_apps = {
            'file explorer': lambda: self._open_file_explorer(),
            'task manager': lambda: self._open_task_manager(),
            'control panel': lambda: self._open_control_panel(),
        }
        
        try:
            # Check for special apps first
            if app_name_lower in special_apps:
                return special_apps[app_name_lower]()
            
            # Check if it's a direct application command
            if app_name_lower in app_commands:
                command = app_commands[app_name_lower]
                
                if self.system == 'windows':
                    if command.endswith('.exe'):
                        subprocess.Popen(command, shell=True)
                    else:
                        subprocess.Popen(f'start {command}', shell=True)
                elif self.system == 'darwin':  # macOS
                    subprocess.Popen(['open', '-a', command])
                else:  # Linux
                    subprocess.Popen([command])
                
                return f"Opening {app_name}..."
            
            # Try to open as a general application
            if self.system == 'windows':
                subprocess.Popen(f'start {app_name}', shell=True)
            elif self.system == 'darwin':
                subprocess.Popen(['open', '-a', app_name])
            else:
                subprocess.Popen([app_name])
            
            return f"Attempting to open {app_name}..."
            
        except Exception as e:
            return f"Error opening {app_name}: {str(e)}"
    
    def _open_file_explorer(self):
        """Open file explorer"""
        if self.system == 'windows':
            subprocess.Popen('explorer .', shell=True)
        elif self.system == 'darwin':
            subprocess.Popen(['open', '.'])
        else:
            subprocess.Popen(['nautilus', '.'])
        return "Opening File Explorer..."
    
    def _open_task_manager(self):
        """Open task manager"""
        if self.system == 'windows':
            subprocess.Popen('taskmgr', shell=True)
        elif self.system == 'darwin':
            subprocess.Popen(['open', '/System/Applications/Utilities/Activity Monitor.app'])
        else:
            subprocess.Popen(['gnome-system-monitor'])
        return "Opening Task Manager..."
    
    def _open_control_panel(self):
        """Open control panel"""
        if self.system == 'windows':
            subprocess.Popen('control', shell=True)
        elif self.system == 'darwin':
            subprocess.Popen(['open', '/System/Applications/System Preferences.app'])
        else:
            subprocess.Popen(['gnome-control-center'])
        return "Opening Control Panel..."
    
    def open_specific_files(self, file_type):
        """Open specific file types or locations"""
        file_type_lower = file_type.lower()
        
        file_locations = {
            'documents': {
                'windows': os.path.expanduser('~/Documents'),
                'darwin': os.path.expanduser('~/Documents'),
                'linux': os.path.expanduser('~/Documents')
            },
            'downloads': {
                'windows': os.path.expanduser('~/Downloads'),
                'darwin': os.path.expanduser('~/Downloads'),
                'linux': os.path.expanduser('~/Downloads')
            },
            'desktop': {
                'windows': os.path.expanduser('~/Desktop'),
                'darwin': os.path.expanduser('~/Desktop'),
                'linux': os.path.expanduser('~/Desktop')
            },
            'pictures': {
                'windows': os.path.expanduser('~/Pictures'),
                'darwin': os.path.expanduser('~/Pictures'),
                'linux': os.path.expanduser('~/Pictures')
            },
            'music': {
                'windows': os.path.expanduser('~/Music'),
                'darwin': os.path.expanduser('~/Music'),
                'linux': os.path.expanduser('~/Music')
            },
            'videos': {
                'windows': os.path.expanduser('~/Videos'),
                'darwin': os.path.expanduser('~/Movies'),
                'linux': os.path.expanduser('~/Videos')
            }
        }
        
        if file_type_lower in file_locations:
            path = file_locations[file_type_lower].get(self.system)
            if path and os.path.exists(path):
                self._open_file_explorer_specific(path)
                return f"Opening {file_type} folder..."
            else:
                return f"{file_type} folder not found."
        
        return f"Unknown location: {file_type}"
    
    def _open_file_explorer_specific(self, path):
        """Open file explorer at specific path"""
        if self.system == 'windows':
            subprocess.Popen(f'explorer "{path}"', shell=True)
        elif self.system == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['nautilus', path])
    
    def route_message(self, message):
        """Route message to appropriate handler"""
        message_lower = message.lower()
        
        # ========== FIXED MUSIC SECTION ==========
        # Music playback commands
        if any(phrase in message_lower for phrase in ['play music', 'play song', 'youtube music', 'play on youtube']):
            return self.play_youtube_music(message)
        
        # Catch all "play [song name]" commands - FIXED CONDITION
        elif message_lower.startswith('play ') and len(message.strip()) > 5:
            return self.play_youtube_music(message)
        # ========== END FIXED MUSIC SECTION ==========
        
        # Screenshot commands
        elif any(word in message_lower for word in ['screenshot', 'capture screen', 'take screenshot']):
            return self.task_manager.take_screenshot()
        
        # Open local applications
        elif any(word in message_lower for word in ['open app', 'launch app', 'start app', 'run app', 'open application']):
            app_name = message_lower.replace('open app', '').replace('launch app', '').replace('start app', '').replace('run app', '').replace('open application', '').strip()
            if app_name:
                return self.open_local_application(app_name)
            else:
                return "Please specify which application to open."
        
        # Open specific applications by name
        elif any(word in message_lower for word in ['open notepad', 'open calculator', 'open paint', 'open file explorer']):
            app_mappings = {
                'notepad': 'notepad',
                'calculator': 'calculator',
                'paint': 'paint',
                'file explorer': 'file explorer',
                'command prompt': 'command prompt',
                'powershell': 'powershell',
                'task manager': 'task manager',
                'control panel': 'control panel',
                'chrome': 'chrome',
                'firefox': 'firefox',
                'vscode': 'vscode',
                'spotify': 'spotify',
                'discord': 'discord'
            }
            
            for app_key, app_value in app_mappings.items():
                if app_key in message_lower:
                    return self.open_local_application(app_value)
        
        # Open file locations
        elif any(word in message_lower for word in ['open documents', 'open downloads', 'open desktop', 'open pictures']):
            location_mappings = {
                'documents': 'documents',
                'downloads': 'downloads',
                'desktop': 'desktop',
                'pictures': 'pictures',
                'music': 'music',
                'videos': 'videos'
            }
            
            for loc_key, loc_value in location_mappings.items():
                if loc_key in message_lower:
                    return self.open_specific_files(loc_value)
        
        # Open websites
        elif any(word in message_lower for word in ['open', 'launch', 'go to']):
            website_mappings = {
                'youtube': 'https://youtube.com',
                'google': 'https://google.com',
                'github': 'https://github.com',
                'instagram': 'https://instagram.com',
                'facebook': 'https://facebook.com',
                'leetcode': 'https://leetcode.com',
                'chatgpt': 'https://chat.openai.com',
                'openai': 'https://openai.com',
                'gemini': 'https://gemini.google.com',
                'amazon': 'https://amazon.com',
                'flipkart': 'https://flipkart.com',
                'weather': 'https://weather.com',
                'gmail': 'https://gmail.com',
                'outlook': 'https://outlook.com',
                'twitter': 'https://twitter.com',
                'linkedin': 'https://linkedin.com',
                'reddit': 'https://reddit.com',
                'whatsapp': 'https://web.whatsapp.com',
                'netflix': 'https://netflix.com',
                'spotify': 'https://spotify.com',
                'stackoverflow': 'https://stackoverflow.com',
                'wikipedia': 'https://wikipedia.org',
                'notion': 'https://notion.so',
                'discord': 'https://discord.com',
                'zoom': 'https://zoom.us',
                'teams': 'https://teams.microsoft.com',
                'slack': 'https://slack.com',
                'figma': 'https://figma.com',
                'canva': 'https://canva.com',
                'dropbox': 'https://dropbox.com',
                'drive': 'https://drive.google.com',
            }
            
            for site_name, site_url in website_mappings.items():
                if site_name in message_lower:
                    return self.task_manager.open_website(site_url)
            
            # If no specific website matched but contains "open website"
            if 'website' in message_lower:
                # Extract URL from message
                import re
                url_pattern = r'https?://[^\s]+'
                urls = re.findall(url_pattern, message)
                if urls:
                    return self.task_manager.open_website(urls[0])
                else:
                    return "Please specify which website to open or provide a URL."
        
        # Math problems
        elif any(word in message_lower for word in ['calculate', 'solve', 'math', 'equation', '+', '-', '*', '/']):
            return self.reasoning_engine.solve_math_problem(message)
        
        # Wikipedia queries
        elif any(word in message_lower for word in ['what is', 'who is', 'tell me about', 'search for', 'look up']):
            topic = message.replace('what is', '').replace('who is', '').replace('tell me about', '').replace('search for', '').replace('look up', '').strip()
            return self.reasoning_engine.get_wikipedia_summary(topic)
        
        # Task management
        elif any(word in message_lower for word in ['add task', 'new task', 'remind me', 'create task']):
            task_text = message.replace('add task', '').replace('new task', '').replace('remind me to', '').replace('remind me', '').replace('create task', '').strip()
            return self.task_manager.add_task(task_text)
        
        # List tasks
        elif any(word in message_lower for word in ['show tasks', 'list tasks', 'my tasks', 'view tasks']):
            tasks = self.task_manager.list_tasks(completed=False)
            if tasks:
                task_list = "\n".join([f"{task[0]}. {task[1]}" for task in tasks])
                return f"Your tasks:\n{task_list}"
            else:
                return "No pending tasks!"
        
        # Complete tasks
        elif any(word in message_lower for word in ['complete task', 'mark done', 'task done']):
            try:
                # Extract task number
                import re
                task_num = re.search(r'\d+', message)
                if task_num:
                    task_id = int(task_num.group())
                    return self.task_manager.complete_task(task_id)
                else:
                    return "Please specify which task to complete (e.g., 'complete task 1')"
            except ValueError:
                return "Please specify a valid task number."
        
        # Weather queries
        elif any(word in message_lower for word in ['weather', 'temperature', 'forecast']):
            # Extract location from message
            location = message_lower.replace('weather', '').replace('temperature', '').replace('forecast', '').replace('in', '').strip()
            if not location:
                location = "current location"
            return f"I can check weather for {location}. Weather service integration would go here."
        
        # Time and date
        elif any(word in message_lower for word in ['time', 'date', 'current time']):
            from datetime import datetime
            now = datetime.now()
            if 'time' in message_lower and 'date' in message_lower:
                return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
            elif 'time' in message_lower:
                return f"Current time: {now.strftime('%H:%M:%S')}"
            else:
                return f"Today's date: {now.strftime('%Y-%m-%d')}"
        
        # System commands
        elif any(word in message_lower for word in ['shutdown', 'restart', 'sleep', 'lock']):
            if 'shutdown' in message_lower:
                return "Shutdown command would go here."
            elif 'restart' in message_lower:
                return "Restart command would go here."
            elif 'sleep' in message_lower:
                return "Sleep command would go here."
            elif 'lock' in message_lower:
                return "Lock screen command would go here."
        
        # General chat
        else:
            return self.chatbot.chat(message)
    
    def voice_input(self):
        def voice_thread():
            try:
                self.root.after(0, lambda: self.display_message("Bot", "Listening..."))
                text = self.utilities.speech_to_text()
                
                if text and not text.startswith("Speech recognition error"):
                    self.root.after(0, lambda: self.user_input.delete(0, tk.END))
                    self.root.after(0, lambda: self.user_input.insert(0, text))
                    self.root.after(0, lambda: self.display_message("Bot", f"Heard: {text}"))
                    # Auto-send after voice input
                    self.root.after(100, self.send_message)
                else:
                    self.root.after(0, lambda: self.display_message("Bot", "Sorry, I didn't catch that. Please try again."))
                    
            except Exception as e:
                self.root.after(0, lambda: self.display_message("Bot", f"Voice input error: {str(e)}"))
        
        threading.Thread(target=voice_thread, daemon=True).start()
    
    def math_solver(self):
        def solve_math():
            problem = self.user_input.get()
            if problem:
                result = self.reasoning_engine.solve_math_problem(problem)
                self.root.after(0, lambda: self.display_message("Bot", f"Math solution: {result}"))
        
        threading.Thread(target=solve_math, daemon=True).start()
    
    def add_task_dialog(self):
        task = simpledialog.askstring("Add Task", "Enter task description:")
        if task:
            result = self.task_manager.add_task(task)
            self.display_message("Bot", result)
    
    def open_app_dialog(self):
        app_name = simpledialog.askstring("Open Application", "Enter application name:")
        if app_name:
            result = self.open_local_application(app_name)
            self.display_message("Bot", result)
    
    def take_screenshot(self):
        result = self.task_manager.take_screenshot()
        self.display_message("Bot", result)
    
    def clear_chat(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.display_message("Bot", "Chat cleared! How can I help you?")

def main():
    try:
        root = tk.Tk()
        app = ChatBotGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()