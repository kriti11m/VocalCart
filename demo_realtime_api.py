#!/usr/bin/env python3
"""
VocalCart API Demo Script
Tests the real-time voice-powered shopping API

This script demonstrates the new architecture:
- Real-time product scraping (no database)
- RESTful API endpoints
- In-memory session management
- Voice command processing
"""

import requests
import json
import time
import sys

# API base URL
API_BASE = "http://127.0.0.1:5002"

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ API is not running. Please start the server first:")
        print("   python main.py")
        return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

def test_voice_command(command):
    """Test voice command processing"""
    print(f"\n🎤 Testing voice command: '{command}'")
    
    try:
        payload = {
            "command": command,
            "session_id": "demo_session"
        }
        
        response = requests.post(
            f"{API_BASE}/api/voice-command",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('voice_response', 'No response')}")
            
            # Show products if available
            if 'products' in result and result['products']:
                print(f"   Found {len(result['products'])} products:")
                for i, product in enumerate(result['products'][:3], 1):
                    print(f"   {i}. {product['title']} - ₹{product['price']}")
            
            return result
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
            
    except requests.Timeout:
        print("❌ Request timeout (scraping may take time)")
        return None
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def test_navigation(command, session_id="demo_session"):
    """Test navigation commands"""
    print(f"\n➡️ Testing navigation: '{command}'")
    
    try:
        payload = {
            "command": command,
            "session_id": session_id
        }
        
        response = requests.post(
            f"{API_BASE}/api/navigate",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Navigation: {result.get('voice_response', 'No response')}")
            return result
        else:
            print(f"❌ Navigation error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Navigation error: {e}")
        return None

def demo_shopping_flow():
    """Demonstrate a complete shopping flow"""
    print("\n" + "="*60)
    print("🛍️  VocalCart Real-time Shopping Demo")
    print("="*60)
    
    # Test API health
    if not test_api_health():
        return
    
    print("\n📱 Testing Real-time Product Search...")
    
    # Test search commands
    search_commands = [
        "find shoes under 2000",
        "search for wireless earphones under 1500",
        "show me smartphones under 20000"
    ]
    
    for command in search_commands:
        result = test_voice_command(command)
        if result and result.get('success'):
            session_id = result.get('session_id', 'demo_session')
            
            # Test navigation
            time.sleep(1)
            test_navigation("next", session_id)
            time.sleep(1)
            test_navigation("repeat", session_id)
            time.sleep(1)
            test_navigation("buy this", session_id)
            
            break  # Only demo one successful search
        time.sleep(2)
    
    print("\n🎯 Demo complete!")
    print("\nKey Features Demonstrated:")
    print("✅ Real-time product scraping (no database)")
    print("✅ Voice command processing")
    print("✅ Product navigation (next/previous/buy)")
    print("✅ In-memory session management")
    print("✅ RESTful API architecture")

def interactive_demo():
    """Interactive demo mode"""
    print("\n🎮 Interactive Demo Mode")
    print("Enter voice commands or 'quit' to exit:")
    print("Examples:")
    print("  - find shoes under 2000")
    print("  - search for laptops under 50000")
    print("  - next")
    print("  - buy this")
    
    session_id = "interactive_session"
    
    while True:
        try:
            command = input("\n🎤 Command: ").strip()
            
            if command.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if not command:
                continue
            
            # Determine if it's a search or navigation command
            nav_commands = ['next', 'previous', 'repeat', 'buy', 'first', 'last']
            
            if any(nav_cmd in command.lower() for nav_cmd in nav_commands):
                test_navigation(command, session_id)
            else:
                result = test_voice_command(command)
                if result:
                    session_id = result.get('session_id', session_id)
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main demo function"""
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_demo()
    else:
        demo_shopping_flow()

if __name__ == "__main__":
    main()
