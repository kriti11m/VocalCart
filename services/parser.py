import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ParsedQuery:
    keywords: str
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None

class QueryParser:
    """
    Enhanced query parser for natural language shopping commands
    Handles price extraction, category detection, and command classification
    """
    
    def __init__(self):
        # Price pattern matching
        self.price_patterns = [
            r'under\s+(?:rs\.?\s*|rupees?\s*|₹\s*)?(\d+)',
            r'below\s+(?:rs\.?\s*|rupees?\s*|₹\s*)?(\d+)',
            r'less\s+than\s+(?:rs\.?\s*|rupees?\s*|₹\s*)?(\d+)',
            r'maximum\s+(?:rs\.?\s*|rupees?\s*|₹\s*)?(\d+)',
            r'max\s+(?:rs\.?\s*|rupees?\s*|₹\s*)?(\d+)',
            r'between\s+(?:rs\.?\s*|rupees?\s*|₹\s*)?(\d+)\s+(?:and|to)\s+(?:rs\.?\s*|rupees?\s*|₹\s*)?(\d+)',
            r'from\s+(?:rs\.?\s*|rupees?\s*|₹\s*)?(\d+)\s+to\s+(?:rs\.?\s*|rupees?\s*|₹\s*)?(\d+)',
            r'(?:rs\.?\s*|rupees?\s*|₹\s*)?(\d+)\s+to\s+(?:rs\.?\s*|rupees?\s*|₹\s*)?(\d+)',
            r'around\s+(?:rs\.?\s*|rupees?\s*|₹\s*)?(\d+)',
            r'about\s+(?:rs\.?\s*|rupees?\s*|₹\s*)?(\d+)'
        ]
        
        # Category keywords
        self.categories = {
            'clothing': ['shirt', 'dress', 'kurti', 'jeans', 'pants', 'top', 'blouse', 'saree', 'suit'],
            'footwear': ['shoes', 'sandals', 'sneakers', 'boots', 'heels', 'flats', 'slippers'],
            'electronics': ['phone', 'laptop', 'tablet', 'headphones', 'earphones', 'speaker', 'charger'],
            'accessories': ['watch', 'bag', 'wallet', 'belt', 'sunglasses', 'jewelry'],
            'home': ['bedsheet', 'pillow', 'curtain', 'lamp', 'mirror', 'furniture'],
            'beauty': ['lipstick', 'foundation', 'perfume', 'cream', 'shampoo', 'makeup']
        }
        
        # Common brands
        self.brands = [
            'nike', 'adidas', 'puma', 'samsung', 'apple', 'oneplus', 'xiaomi',
            'realme', 'vivo', 'oppo', 'sony', 'lg', 'hp', 'dell', 'lenovo',
            'asus', 'acer', 'boat', 'jbl', 'bose', 'fossil', 'titan'
        ]
        
        # Colors
        self.colors = [
            'red', 'blue', 'green', 'yellow', 'black', 'white', 'grey', 'gray',
            'pink', 'purple', 'orange', 'brown', 'navy', 'maroon', 'olive'
        ]
        
        # Command types
        self.search_commands = [
            'find', 'search', 'look for', 'show me', 'get me', 'i want', 'need'
        ]
        
        self.navigation_commands = [
            'next', 'previous', 'prev', 'back', 'repeat', 'again', 'first', 'last'
        ]
        
        self.action_commands = [
            'buy', 'purchase', 'add to cart', 'cart', 'order', 'book'
        ]
        
        self.info_commands = [
            'details', 'info', 'information', 'tell me about', 'describe', 'specs'
        ]
    
    def parse_search_query(self, query: str, min_price: Optional[int] = None, max_price: Optional[int] = None) -> Dict:
        """
        Parse a search query and extract structured information
        """
        query_lower = query.lower().strip()
        
        # Extract price information
        extracted_min_price, extracted_max_price = self._extract_price_range(query_lower)
        
        # Use provided prices if extraction failed
        final_min_price = min_price or extracted_min_price
        final_max_price = max_price or extracted_max_price
        
        # Extract category
        category = self._extract_category(query_lower)
        
        # Extract brand
        brand = self._extract_brand(query_lower)
        
        # Extract color
        color = self._extract_color(query_lower)
        
        # Clean keywords (remove price and category info)
        clean_keywords = self._clean_keywords(query_lower)
        
        return {
            "keywords": clean_keywords,
            "min_price": final_min_price,
            "max_price": final_max_price,
            "category": category,
            "brand": brand,
            "color": color,
            "original_query": query
        }
    
    def parse_command_type(self, command: str) -> Dict:
        """
        Determine the type of command (search, navigation, action, info)
        """
        command_lower = command.lower().strip()
        
        # Check for navigation commands
        for nav_cmd in self.navigation_commands:
            if nav_cmd in command_lower:
                return {
                    "type": "navigation",
                    "command": nav_cmd,
                    "original": command
                }
        
        # Check for action commands
        for action_cmd in self.action_commands:
            if action_cmd in command_lower:
                return {
                    "type": "action",
                    "command": action_cmd,
                    "original": command
                }
        
        # Check for info commands
        for info_cmd in self.info_commands:
            if info_cmd in command_lower:
                return {
                    "type": "info",
                    "command": info_cmd,
                    "original": command
                }
        
        # Check for search commands
        for search_cmd in self.search_commands:
            if search_cmd in command_lower:
                return {
                    "type": "search",
                    "command": search_cmd,
                    "original": command
                }
        
        # Default to search if no specific command detected
        return {
            "type": "search",
            "command": "search",
            "original": command
        }
    
    def _extract_price_range(self, query: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract min and max price from query"""
        min_price = None
        max_price = None
        
        for pattern in self.price_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if 'between' in pattern or 'from' in pattern or 'to' in pattern:
                    # Range patterns
                    try:
                        min_price = int(match.group(1))
                        max_price = int(match.group(2))
                    except (IndexError, ValueError):
                        continue
                elif 'under' in pattern or 'below' in pattern or 'less' in pattern or 'max' in pattern:
                    # Upper limit patterns
                    try:
                        max_price = int(match.group(1))
                    except (IndexError, ValueError):
                        continue
                elif 'around' in pattern or 'about' in pattern:
                    # Approximate price patterns
                    try:
                        price = int(match.group(1))
                        min_price = int(price * 0.8)  # 20% below
                        max_price = int(price * 1.2)  # 20% above
                    except (IndexError, ValueError):
                        continue
                break
        
        return min_price, max_price
    
    def _extract_category(self, query: str) -> Optional[str]:
        """Extract product category from query"""
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in query:
                    return category
        return None
    
    def _extract_brand(self, query: str) -> Optional[str]:
        """Extract brand from query"""
        for brand in self.brands:
            if brand in query:
                return brand
        return None
    
    def _extract_color(self, query: str) -> Optional[str]:
        """Extract color from query"""
        for color in self.colors:
            if color in query:
                return color
        return None
    
    def _clean_keywords(self, query: str) -> str:
        """Clean the query to get main keywords"""
        # Remove price information
        for pattern in self.price_patterns:
            query = re.sub(pattern, '', query, flags=re.IGNORECASE)
        
        # Remove common stop words and command words
        stop_words = ['find', 'search', 'show', 'me', 'get', 'i', 'want', 'need', 'for', 'a', 'an', 'the']
        words = query.split()
        clean_words = [word for word in words if word not in stop_words and len(word) > 1]
        
        return ' '.join(clean_words).strip()
    
    def extract_item_number(self, command: str) -> Optional[int]:
        """Extract item number from navigation commands like 'show item 3'"""
        patterns = [
            r'item\s+(\d+)',
            r'number\s+(\d+)',
            r'option\s+(\d+)',
            r'product\s+(\d+)',
            r'(\d+)(?:st|nd|rd|th)?\s+(?:item|option|product)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, command.lower())
            if match:
                try:
                    return int(match.group(1))
                except (IndexError, ValueError):
                    continue
        
        return None
    
    def is_exit_command(self, command: str) -> bool:
        """Check if command is to exit the application"""
        exit_phrases = ['exit', 'quit', 'bye', 'goodbye', 'stop', 'end', 'close']
        command_lower = command.lower().strip()
        return any(phrase in command_lower for phrase in exit_phrases)
