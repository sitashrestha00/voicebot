import json
import random
from difflib import get_close_matches
import pyttsx3
import speech_recognition as sr
import time

class CollegeAssistant:
    def __init__(self, intents_file="intents.json"):
        self.intents = self.load_intents(intents_file)
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        # Initialize recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        # Adjust for ambient noise
        with self.microphone as source:
            print("Calibrating microphone...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def load_intents(self, file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            return data["intents"]
        except Exception as e:
            self.speak(f"Error loading intents: {str(e)}")
            return []
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self):
        """Listen to microphone and return recognized text"""
        with self.microphone as source:
            print("Listening...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                try:
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"You said: {text}")
                    return text
                except sr.UnknownValueError:
                    self.speak("Sorry, I didn't understand that.")
                except sr.RequestError:
                    self.speak("Sorry, my speech service is unavailable.")
            except sr.WaitTimeoutError:
                self.speak("I didn't hear anything. Please try again.")
        return None
    
    def get_response(self, user_input):
        if not user_input:
            return None
            
        user_input = user_input.lower()
        
        # Check for exact matches
        for intent in self.intents:
            if user_input in [p.lower() for p in intent["patterns"]]:
                return random.choice(intent["responses"])
        
        # Check for similar patterns
        all_patterns = []
        for intent in self.intents:
            all_patterns.extend(intent["patterns"])
        
        matches = get_close_matches(user_input, [p.lower() for p in all_patterns], n=1, cutoff=0.6)
        
        if matches:
            for intent in self.intents:
                if matches[0] in [p.lower() for p in intent["patterns"]]:
                    return random.choice(intent["responses"])
        
        return "I'm not sure I understand. Could you rephrase that?"

    def run(self):
        self.speak("Hello! I'm your College Assistant. How can I help you? Please speak your question or press 'Ctrl+c' to exit.")
        
        while True:
            # self.speak("Please speak your question or say 'quit' to exit.")
            user_input = self.listen()
            
            # Fallback to text input if voice fails
            if not user_input:
                try:
                    user_input = input("Or type your question here: ")
                except KeyboardInterrupt:
                    self.speak("Goodbye!")
                    break
            
            if user_input and user_input.lower() == 'quit':
                self.speak("Goodbye! Have a great day!")
                break
                
            if user_input:
                response = self.get_response(user_input)
                if response:
                    self.speak(response)
                    time.sleep(1)  # Pause between responses

if __name__ == "__main__":
    assistant = CollegeAssistant()
    try:
        assistant.run()
    except KeyboardInterrupt:
        assistant.speak("Assistant shutting down.")
    except Exception as e:
        print(f"Error: {str(e)}")
        assistant.speak("Sorry, I encountered an error.")