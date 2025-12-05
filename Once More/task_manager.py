import sqlite3
import json
import pyautogui
import os
import webbrowser
from datetime import datetime, timedelta

class TaskManager:
    def __init__(self):
        self.setup_task_database()
    
    def setup_task_database(self):
        """Initialize task database"""
        self.conn = sqlite3.connect('tasks.db', check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                category TEXT,
                due_date TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_at TEXT
            )
        ''')
        self.conn.commit()
    
    def add_task(self, task, category="general", due_date=None):
        """Add a new task"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (task, category, due_date, created_at)
            VALUES (?, ?, ?, ?)
        ''', (task, category, due_date, datetime.now().isoformat()))
        self.conn.commit()
        return f"Task added: {task}"
    
    def list_tasks(self, category=None, completed=False):
        """List tasks with optional filtering"""
        cursor = self.conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT id, task, category, due_date FROM tasks 
                WHERE completed = ? AND category = ?
            ''', (completed, category))
        else:
            cursor.execute('''
                SELECT id, task, category, due_date FROM tasks 
                WHERE completed = ?
            ''', (completed,))
        
        tasks = cursor.fetchall()
        return tasks
    
    def complete_task(self, task_id):
        """Mark task as completed"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE tasks SET completed = TRUE WHERE id = ?', (task_id,))
        self.conn.commit()
        return "Task marked as completed"
    
    def take_screenshot(self, filename=None):
        """Take a screenshot"""
        try:
            if not filename:
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            return f"Screenshot saved as {filename}"
        except Exception as e:
            return f"Error taking screenshot: {str(e)}"
    
    def open_website(self, url):
        """Open websites in browser"""
        try:
            webbrowser.open(url)
            return f"Opened {url}"
        except Exception as e:
            return f"Could not open {url}: {str(e)}"
    
    def open_application(self, app_name):
        """Open common applications"""
        apps = {
            'notepad': 'notepad.exe',
            'calculator': 'calc.exe',
            'paint': 'mspaint.exe',
            'cmd': 'cmd.exe',
            'browser': 'msedge.exe'
        }
        
        app_name_lower = app_name.lower()
        if app_name_lower in apps:
            try:
                os.system(f'start {apps[app_name_lower]}')
                return f"Opening {app_name}"
            except:
                return f"Could not open {app_name}"
        else:
            return f"Don't know how to open {app_name}"
    
    def get_pending_tasks_count(self):
        """Get count of pending tasks"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE completed = FALSE')
        count = cursor.fetchone()[0]
        return count
    
    def delete_task(self, task_id):
        """Delete a task"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        return "Task deleted"