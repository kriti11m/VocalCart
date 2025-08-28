#!/usr/bin/env python3
"""
Complete VocalCart Demo - Real-time Voice Shopping System
==========================================================

This demo shows the complete VocalCart system working with:
1. Voice input and output
2. Real-time product search (with realistic demo data when network issues occur)
3. Shopping cart management
4. Voice navigation

The system is designed to work with real e-commerce scraping, but includes
intelligent fallbacks for network connectivity issues.
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import speech_recognition as sr
    import pyttsx3
    import requests
    from typing import Dict, List, Optional
    print("✅ All voice libraries imported successfully")
except ImportError as e:
    print(f"❌ Missing voice libraries: {e}")
    print("Install with: pip install speechrecognition pyttsx3 pyaudio")
    sys.exit(1)

class VocalCartDemo:
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.session_id = f"demo_{int(time.time())}"
        self.current_products = []
        self.current_index = 0
        
        # Initialize voice components
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        
        # Configure TTS
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.9)
        
        print(f"🎯 VocalCart Demo initialized with session: {self.session_id}")
    
    def speak(self, text: str):
        """Convert text to speech"""
        print(f"🔊 Speaking: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self) -> Optional[str]:
        """Listen for voice input"""
        try:
            print("🎤 Listening... (speak now)")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            print("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"📝 You said: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected, continuing...")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand audio")
            self.speak("Sorry, I didn't understand that. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            self.speak("Speech recognition service unavailable")
            return None
    
    def search_products(self, query: str) -> bool:
        """Search for products using the API"""
        try:
            print(f"🔍 Searching for: {query}")
            
            response = requests.post(
                f"{self.api_base}/search",
                json={
                    "query": query,
                    "session_id": self.session_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.current_products = data.get('products', [])
                self.current_index = 0
                
                if self.current_products:
                    self.speak(f"Found {len(self.current_products)} products for {query}")
                    return True
                else:
                    self.speak(f"No products found for {query}")
                    return False
            else:
                print(f"❌ Search API error: {response.status_code}")
                self.speak("Search service temporarily unavailable")
                return False
                
        except requests.exceptions.Timeout:
            print("⏰ Search request timed out")
            self.speak("Search is taking too long. Please try again.")
            return False
        except Exception as e:
            print(f"❌ Search error: {e}")
            self.speak("Search encountered an error")
            return False
    
    def describe_current_product(self):
        """Describe the currently selected product"""
        if not self.current_products or self.current_index >= len(self.current_products):
            self.speak("No product selected")
            return
        
        product = self.current_products[self.current_index]
        
        # Build description
        name = product.get('name', 'Unknown product')
        price = product.get('price', 'Price not available')
        rating = product.get('rating', 'No rating')
        brand = product.get('brand', '')
        
        description = f"Product {self.current_index + 1} of {len(self.current_products)}. "
        if brand:
            description += f"{brand} "
        description += f"{name}. "
        description += f"Price: {price}. "
        description += f"Rating: {rating} stars."
        
        if product.get('discount'):
            description += f" {product.get('discount')} discount available."
        
        print(f"📦 Current product: {description}")
        self.speak(description)
    
    def navigate_products(self, direction: str) -> bool:
        """Navigate through products"""
        if not self.current_products:
            self.speak("No products to navigate")
            return False
        
        if direction == "next":
            if self.current_index < len(self.current_products) - 1:
                self.current_index += 1
                self.speak("Next product")
                self.describe_current_product()
                return True
            else:
                self.speak("This is the last product")
                return False
        
        elif direction == "previous":
            if self.current_index > 0:
                self.current_index -= 1
                self.speak("Previous product")
                self.describe_current_product()
                return True
            else:
                self.speak("This is the first product")
                return False
        
        return False
    
    def add_to_cart(self):
        """Add current product to cart"""
        if not self.current_products or self.current_index >= len(self.current_products):
            self.speak("No product selected to add to cart")
            return False
        
        try:
            product = self.current_products[self.current_index]
            
            response = requests.post(
                f"{self.api_base}/navigate",
                json={
                    "command": "add_to_cart",
                    "session_id": self.session_id,
                    "product_index": self.current_index
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    product_name = product.get('name', 'Product')
                    self.speak(f"Added {product_name} to your cart")
                    return True
                else:
                    self.speak("Failed to add product to cart")
                    return False
            else:
                self.speak("Cart service unavailable")
                return False
                
        except Exception as e:
            print(f"❌ Add to cart error: {e}")
            self.speak("Error adding to cart")
            return False
    
    def view_cart(self):
        """View shopping cart contents"""
        try:
            response = requests.get(
                f"{self.api_base}/navigate",
                params={"session_id": self.session_id, "command": "view_cart"},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                cart_items = data.get('cart', [])
                
                if not cart_items:
                    self.speak("Your cart is empty")
                    return
                
                cart_description = f"You have {len(cart_items)} items in your cart. "
                total_price = 0
                
                for i, item in enumerate(cart_items):
                    name = item.get('name', 'Unknown item')
                    # Extract numeric price
                    price_str = item.get('price', '₹0')
                    try:
                        price_num = int(''.join(filter(str.isdigit, price_str)))
                        total_price += price_num
                    except:
                        pass
                    
                    cart_description += f"Item {i+1}: {name}. "
                
                if total_price > 0:
                    cart_description += f"Total: ₹{total_price:,}."
                
                self.speak(cart_description)
                
            else:
                self.speak("Cart service unavailable")
                
        except Exception as e:
            print(f"❌ View cart error: {e}")
            self.speak("Error viewing cart")
    
    def process_voice_command(self, command: str) -> bool:
        """Process voice commands and return True if should continue"""
        command = command.lower().strip()
        
        # Exit commands
        if any(word in command for word in ['exit', 'quit', 'stop', 'bye', 'goodbye']):
            self.speak("Thank you for using VocalCart. Goodbye!")
            return False
        
        # Help command
        elif 'help' in command:
            help_text = """
            Available commands:
            - Search for shoes, phones, laptops, or any product
            - Say next or previous to navigate products
            - Say add to cart to add current product
            - Say view cart to see cart contents
            - Say help for this message
            - Say exit to quit
            """
            self.speak("Here are the available commands")
            print(help_text)
            return True
        
        # Search commands
        elif any(word in command for word in ['search', 'find', 'look for']):
            # Extract search query
            search_words = ['search for', 'find', 'look for', 'search']
            query = command
            for word in search_words:
                if word in query:
                    query = query.split(word, 1)[-1].strip()
                    break
            
            if query:
                if self.search_products(query):
                    self.describe_current_product()
            else:
                self.speak("What would you like to search for?")
            return True
        
        # Direct product searches
        elif any(word in command for word in ['shoes', 'phone', 'laptop', 'headphones', 'mobile']):
            if self.search_products(command):
                self.describe_current_product()
            return True
        
        # Navigation commands
        elif 'next' in command:
            self.navigate_products('next')
            return True
        
        elif 'previous' in command or 'back' in command:
            self.navigate_products('previous')
            return True
        
        # Cart commands
        elif 'add to cart' in command or 'add cart' in command:
            self.add_to_cart()
            return True
        
        elif 'view cart' in command or 'show cart' in command or 'cart' in command:
            self.view_cart()
            return True
        
        # Repeat current product
        elif any(word in command for word in ['repeat', 'again', 'current']):
            self.describe_current_product()
            return True
        
        else:
            self.speak("I didn't understand that command. Say help for available commands.")
            return True
    
    def run_demo(self):
        """Run the complete demo"""
        print("\n" + "="*60)
        print("🛒 VocalCart - Voice Shopping Demo")
        print("="*60)
        
        # Check if server is running
        try:
            response = requests.get(f"{self.api_base}/", timeout=5)
            print("✅ VocalCart server is running")
        except:
            print("❌ VocalCart server not running. Start with: python fastapi_server.py")
            return
        
        # Welcome message
        welcome_msg = """
        Welcome to VocalCart! Your voice-powered shopping assistant.
        
        You can:
        - Search for products: 'search for shoes' or just say 'shoes'
        - Navigate: 'next' or 'previous'
        - Add to cart: 'add to cart'
        - View cart: 'view cart'
        - Get help: 'help'
        - Exit: 'exit'
        
        Let's start shopping! What would you like to search for?
        """
        
        print(welcome_msg)
        self.speak("Welcome to VocalCart! What would you like to search for?")
        
        # Demo loop
        while True:
            try:
                # Listen for command
                command = self.listen()
                
                if command:
                    # Process command
                    should_continue = self.process_voice_command(command)
                    if not should_continue:
                        break
                else:
                    # If no voice input, wait a bit and continue
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n👋 Demo interrupted by user")
                self.speak("Demo stopped. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Demo error: {e}")
                self.speak("Something went wrong. Let's continue.")
                continue
        
        print("\n🎉 VocalCart Demo completed!")

def main():
    """Main demo function"""
    try:
        demo = VocalCartDemo()
        demo.run_demo()
    except Exception as e:
        print(f"❌ Failed to start demo: {e}")
        print("Make sure you have installed: pip install speechrecognition pyttsx3 pyaudio")
        print("And that the VocalCart server is running: python fastapi_server.py")

if __name__ == "__main__":
    main()
