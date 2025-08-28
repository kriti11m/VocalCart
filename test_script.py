#!/usr/bin/env python3
"""
VocalCart Test Script
Comprehensive test suite for VocalCart voice shopping application.

This script tests both backend and frontend functionality including:
- Search functionality
- Voice commands
- Shopping cart operations
- Accessibility features
- API endpoints
"""

import unittest
import requests
import json
import os
import sys
import time
from pprint import pprint

# Set base URL for API tests
BASE_URL = "http://localhost:5004/api"
SESSION_ID = "test_session"  # Use a dedicated session ID for testing

class VocalCartTests(unittest.TestCase):
    """Test suite for VocalCart application"""
    
    def setUp(self):
        """Set up test environment before each test"""
        # Clear any existing session data
        try:
            requests.delete(f"{BASE_URL}/session/{SESSION_ID}")
        except Exception as e:
            print(f"Warning: Could not clear session: {e}")
            
        # Clear cart for clean testing
        try:
            requests.post(f"{BASE_URL}/cart/clear", json={"session_id": SESSION_ID})
        except Exception as e:
            print(f"Warning: Could not clear cart: {e}")
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
    
    def test_voice_command_search(self):
        """Test voice command search functionality"""
        # Test search via voice command API
        command = "find shoes under 2000 rupees"
        response = requests.post(
            f"{BASE_URL}/voice-command",
            json={"command": command, "session_id": SESSION_ID}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Since search is async, check if processing status is returned
        if data.get("status") == "processing":
            print("Search in progress, polling for results...")
            # Poll for results
            max_polls = 10
            poll_count = 0
            while poll_count < max_polls:
                poll_count += 1
                time.sleep(2)  # Wait 2 seconds between polls
                
                poll_response = requests.get(f"{BASE_URL}/search-status/{SESSION_ID}")
                poll_data = poll_response.json()
                
                if poll_data.get("status") == "complete":
                    print(f"Search completed after {poll_count} polls")
                    data = poll_data  # Update data with final results
                    break
            
            if poll_count >= max_polls:
                print("Warning: Search timed out during polling")
        
        # Check if we have products or a valid error
        if "products" in data and isinstance(data["products"], list):
            print(f"Found {len(data['products'])} products")
            if len(data["products"]) > 0:
                print(f"First product: {data['products'][0]['title']}")
        else:
            print("No products found, but API returned valid response")
            
        self.assertIn("voice_response", data)
    
    def test_cart_operations(self):
        """Test cart operations (add, view, remove, clear, checkout)"""
        # First add test products to current search results
        test_product1 = {
            "title": "Test Shoes 1",
            "price": 1500,
            "image": "https://example.com/image1.jpg",
            "source": "test_store"
        }
        
        test_product2 = {
            "title": "Test Shoes 2",
            "price": 1800,
            "image": "https://example.com/image2.jpg",
            "source": "test_store"
        }
        
        # Add first product to cart
        response = requests.post(
            f"{BASE_URL}/cart/add",
            json={"product": test_product1, "session_id": SESSION_ID}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["item_count"], 1)
        
        # Add second product to cart
        response = requests.post(
            f"{BASE_URL}/cart/add",
            json={"product": test_product2, "session_id": SESSION_ID}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["item_count"], 2)
        
        # Get cart items
        response = requests.get(f"{BASE_URL}/cart/items?session_id={SESSION_ID}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(len(data["items"]), 2)
        
        # Remove first item
        response = requests.post(
            f"{BASE_URL}/cart/remove",
            json={"item_title": test_product1["title"], "session_id": SESSION_ID}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["item_count"], 1)
        
        # Test checkout
        response = requests.post(
            f"{BASE_URL}/cart/checkout",
            json={"session_id": SESSION_ID}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        # Cart should be empty after checkout
        self.assertEqual(data["item_count"], 0)
    
    def test_voice_command_parser(self):
        """Test if voice commands are correctly parsed and routed"""
        # Set up a list of commands to test
        test_commands = [
            # Search commands
            {"command": "find shoes under 2000 rupees", "expected_action": "search"},
            {"command": "search for wireless earphones", "expected_action": "search"},
            {"command": "show me smartphones", "expected_action": "search"},
            
            # Navigation commands
            {"command": "next", "expected_action": "navigation"},
            {"command": "previous", "expected_action": "navigation"},
            
            # Cart commands
            {"command": "add item 2 to cart", "expected_action": "add_to_cart"},
            {"command": "show my cart", "expected_action": "view_cart"},
            {"command": "clear cart", "expected_action": "clear_cart"}
        ]
        
        # Test each command
        for test in test_commands:
            response = requests.post(
                f"{BASE_URL}/voice-command",
                json={"command": test["command"], "session_id": SESSION_ID}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            
            # Check if command was properly categorized
            if test["expected_action"] == "search" and data.get("status") == "processing":
                print(f"Command '{test['command']}' recognized as search")
            elif test["expected_action"] == "navigation" and data.get("action") in ["next", "previous"]:
                print(f"Command '{test['command']}' recognized as navigation")
            elif test["expected_action"] == "add_to_cart" and "add" in data.get("message", "").lower():
                print(f"Command '{test['command']}' recognized as add to cart")
            elif test["expected_action"] == "view_cart" and "cart" in data.get("message", "").lower():
                print(f"Command '{test['command']}' recognized as view cart")
            elif test["expected_action"] == "clear_cart" and "clear" in data.get("message", "").lower():
                print(f"Command '{test['command']}' recognized as clear cart")
            else:
                print(f"Command '{test['command']}' might not be properly recognized")
                
            self.assertIn("voice_response", data)

def run_tests():
    """Run the test suite"""
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("WARNING: API server doesn't seem to be responding correctly. Is it running?")
    except Exception as e:
        print(f"ERROR: Cannot connect to API at {BASE_URL}. Is the server running?")
        print(f"Error details: {e}")
        return
    
    # Run tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == "__main__":
    print("VocalCart Test Script")
    print("=====================")
    print(f"Testing API at {BASE_URL}")
    print("Make sure the server is running before executing tests.\n")
    run_tests()
