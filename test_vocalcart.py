#!/usr/bin/env python3
"""
VocalCart Test Script
Tests the key functionality of the VocalCart system
"""

import argparse
import requests
import json
import time
import os
import sys
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vocalcart-test")

# Default API URL
API_URL = "http://localhost:5004/api"

class VocalCartTester:
    """Test VocalCart functionality"""
    
    def __init__(self, api_url=API_URL, session_id="test_session"):
        """Initialize tester with API URL"""
        self.api_url = api_url
        self.session_id = session_id
        logger.info(f"Testing VocalCart API at: {api_url}")
        
    def test_health(self) -> bool:
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.api_url}/health")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"API Health: {data['status']} - {data['service']}")
                return True
            else:
                logger.error(f"Health check failed with status: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False
    
    def test_search(self, query: str) -> Dict[str, Any]:
        """Test search functionality"""
        try:
            logger.info(f"Testing search for: '{query}'")
            payload = {
                "command": query,
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.api_url}/voice-command", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    products = data.get("products", [])
                    logger.info(f"Search successful! Found {len(products)} products")
                    if products:
                        sample = products[0]
                        logger.info(f"Sample product: {sample.get('title', 'Unknown')} - ₹{sample.get('price', 'Unknown')}")
                else:
                    logger.warning(f"Search failed: {data.get('error', 'Unknown error')}")
                    
                return data
            else:
                logger.error(f"Search failed with status: {response.status_code}")
                return {"success": False, "error": f"HTTP error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"success": False, "error": str(e)}
    
    def test_navigate(self, command: str) -> Dict[str, Any]:
        """Test navigation functionality"""
        try:
            logger.info(f"Testing navigation: '{command}'")
            payload = {
                "command": command,
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.api_url}/navigate", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    logger.info(f"Navigation successful: {command}")
                    product = data.get("product", {})
                    if product:
                        logger.info(f"Current product: {product.get('title', 'Unknown')} - ₹{product.get('price', 'Unknown')}")
                else:
                    logger.warning(f"Navigation failed: {data.get('message', 'Unknown error')}")
                return data
            else:
                logger.error(f"Navigation failed with status: {response.status_code}")
                return {"success": False, "error": f"HTTP error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return {"success": False, "error": str(e)}
    
    def test_cart_add(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Test adding product to cart"""
        try:
            logger.info(f"Adding to cart: {product.get('title', 'Unknown product')}")
            payload = {
                "product": product,
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.api_url}/cart/add", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    logger.info(f"Added to cart successfully! Cart now has {data.get('cart_size', 0)} items")
                else:
                    logger.warning(f"Failed to add to cart: {data.get('message', 'Unknown error')}")
                return data
            else:
                logger.error(f"Add to cart failed with status: {response.status_code}")
                return {"success": False, "error": f"HTTP error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Add to cart error: {e}")
            return {"success": False, "error": str(e)}
    
    def test_cart_items(self) -> List[Dict[str, Any]]:
        """Test getting cart items"""
        try:
            logger.info("Getting cart items")
            
            response = requests.get(f"{self.api_url}/cart/items", params={"session_id": self.session_id})
            if response.status_code == 200:
                items = response.json()
                logger.info(f"Cart has {len(items)} items")
                for i, item in enumerate(items, 1):
                    logger.info(f"  {i}. {item.get('title', 'Unknown')} - ₹{item.get('price', 'Unknown')}")
                return items
            else:
                logger.error(f"Get cart items failed with status: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Get cart items error: {e}")
            return []
    
    def test_cart_remove(self, title: str) -> Dict[str, Any]:
        """Test removing item from cart"""
        try:
            logger.info(f"Removing from cart: {title}")
            payload = {
                "item_title": title,
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.api_url}/cart/remove", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    logger.info(f"Item removed successfully! Cart now has {data.get('cart_size', 0)} items")
                else:
                    logger.warning(f"Failed to remove from cart: {data.get('message', 'Unknown error')}")
                return data
            else:
                logger.error(f"Remove from cart failed with status: {response.status_code}")
                return {"success": False, "error": f"HTTP error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Remove from cart error: {e}")
            return {"success": False, "error": str(e)}
    
    def test_cart_clear(self) -> Dict[str, Any]:
        """Test clearing cart"""
        try:
            logger.info("Clearing cart")
            payload = {
                "session_id": self.session_id
            }
            
            response = requests.post(f"{self.api_url}/cart/clear", json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    logger.info("Cart cleared successfully!")
                else:
                    logger.warning(f"Failed to clear cart: {data.get('message', 'Unknown error')}")
                return data
            else:
                logger.error(f"Clear cart failed with status: {response.status_code}")
                return {"success": False, "error": f"HTTP error: {response.status_code}"}
        except Exception as e:
            logger.error(f"Clear cart error: {e}")
            return {"success": False, "error": str(e)}
    
    def run_simple_test(self) -> bool:
        """Run a simple test flow"""
        try:
            # 1. Check API health
            if not self.test_health():
                logger.error("Health check failed, aborting test")
                return False
            
            # 2. Search for products
            search_result = self.test_search("find wireless earphones under 2000")
            if not search_result.get("success", False):
                logger.error("Search test failed, aborting test")
                return False
            
            # 3. Navigate through products
            self.test_navigate("next")
            self.test_navigate("next")
            self.test_navigate("previous")
            
            # 4. Add to cart
            if search_result.get("products"):
                product = search_result["products"][0]
                self.test_cart_add(product)
                
                # Try adding another product if available
                if len(search_result["products"]) > 1:
                    self.test_cart_add(search_result["products"][1])
            
            # 5. Check cart items
            self.test_cart_items()
            
            # 6. Remove an item
            items = self.test_cart_items()
            if items:
                self.test_cart_remove(items[0]["title"])
            
            # 7. Clear cart
            self.test_cart_clear()
            
            logger.info("Test completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Test error: {e}")
            return False
    
    def run_interactive(self):
        """Run interactive test mode"""
        print("\n" + "="*60)
        print("VocalCart Interactive Test Mode")
        print("="*60)
        
        # Check API health
        if not self.test_health():
            print("\n❌ API is not responding. Make sure the server is running.")
            return
        
        while True:
            print("\nCommands:")
            print("1. Search for products")
            print("2. Navigate (next/previous/repeat)")
            print("3. View cart")
            print("4. Add current product to cart")
            print("5. Remove from cart")
            print("6. Clear cart")
            print("7. Run full test")
            print("8. Exit")
            
            choice = input("\nEnter command (1-8): ").strip()
            
            if choice == "1":
                query = input("Enter search query: ")
                self.test_search(query)
                
            elif choice == "2":
                nav = input("Enter navigation (next/previous/repeat): ")
                self.test_navigate(nav)
                
            elif choice == "3":
                self.test_cart_items()
                
            elif choice == "4":
                # Get current product from session
                try:
                    response = requests.get(f"{self.api_url}/session/{self.session_id}")
                    if response.status_code == 200:
                        session_data = response.json()
                        current_index = session_data.get("current_index", 0)
                        
                        # Get products
                        response = requests.post(f"{self.api_url}/voice-command", 
                                                json={"command": "repeat", "session_id": self.session_id})
                        if response.status_code == 200:
                            data = response.json()
                            products = data.get("products", [])
                            if products and current_index < len(products):
                                self.test_cart_add(products[current_index])
                            else:
                                print("No current product. Search for products first.")
                    else:
                        print("No session found. Search for products first.")
                except Exception as e:
                    print(f"Error: {e}")
                
            elif choice == "5":
                items = self.test_cart_items()
                if items:
                    index = input(f"Enter item number to remove (1-{len(items)}): ")
                    try:
                        index = int(index) - 1
                        if 0 <= index < len(items):
                            self.test_cart_remove(items[index]["title"])
                        else:
                            print("Invalid item number")
                    except:
                        print("Invalid input")
                else:
                    print("Cart is empty")
                
            elif choice == "6":
                self.test_cart_clear()
                
            elif choice == "7":
                self.run_simple_test()
                
            elif choice == "8":
                print("Exiting...")
                break
                
            else:
                print("Invalid command")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="VocalCart Test Script")
    parser.add_argument("--url", default=API_URL, help="API URL")
    parser.add_argument("--session", default="test_session", help="Session ID")
    parser.add_argument("mode", nargs="?", choices=["simple", "interactive"], default="simple", help="Test mode")
    
    args = parser.parse_args()
    
    # Create tester
    tester = VocalCartTester(api_url=args.url, session_id=args.session)
    
    # Run tests
    if args.mode == "interactive":
        tester.run_interactive()
    else:
        tester.run_simple_test()

if __name__ == "__main__":
    main()
