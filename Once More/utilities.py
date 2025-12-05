import speech_recognition as sr
import pyttsx3
import requests
import json
import os
from datetime import datetime, timedelta

class Utilities:
    def __init__(self):
        try:
            self.tts_engine = pyttsx3.init()
            self.recognizer = sr.Recognizer()
            self.has_voice = True
        except Exception as e:
            print(f"Voice initialization failed: {e}")
            self.has_voice = False
    
    def text_to_speech(self, text):
        """Convert text to speech"""
        if not self.has_voice:
            return "Voice features not available"
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return "Speech completed"
        except Exception as e:
            return f"Speech error: {str(e)}"
    
    def speech_to_text(self):
        """Convert speech to text"""
        if not self.has_voice:
            return "Voice features not available"
        
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.recognizer.listen(source)
                text = self.recognizer.recognize_google(audio)
                return text
        except Exception as e:
            return f"Speech recognition error: {str(e)}"
    
    def get_weather(self, city):
        """Get weather information placeholder"""
        return f"Weather API not configured for {city}."
    
    def calculate(self, expression):
        """Basic calculator"""
        try:
            allowed_chars = set('0123456789+-*/.() ')
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return f"Result: {result}"
            else:
                return "Invalid expression for calculation"
        except:
            return "Could not calculate the expression"
    
    def set_reminder(self, reminder_text, minutes_from_now):
        """Set a simple reminder"""
        reminder_time = datetime.now() + timedelta(minutes=minutes_from_now)
        return f"Reminder set for {reminder_time.strftime('%H:%M')}: {reminder_text}"
    
    def open_website(self, site_name):
        """Open common websites"""
        import webbrowser
        sites = {
            'youtube': 'https://youtube.com',
            'google': 'https://google.com',
            'github': 'https://github.com',
            'gmail': 'https://gmail.com'
        }
        
        if site_name.lower() in sites:
            webbrowser.open(sites[site_name.lower()])
            return f"Opening {site_name}"
        else:
            return f"Don't know how to open {site_name}"