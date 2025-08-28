import re
import json
from typing import Dict, List, Tuple, Any
from collections import defaultdict

# Try to import spaCy, but make it optional
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

class AdvancedNLPEngine:
    """
    Advanced Natural Language Processing Engine for VocalCart
    Implements intent recognition, entity extraction, and query understanding
    Designed specifically for voice-based e-commerce interactions
    """
    
    def __init__(self):
        # Try to load spaCy model, fallback to basic processing if not available
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                self.use_spacy = True
            except:
                print("spaCy model not found. Using basic NLP processing.")
                self.use_spacy = False
                self.nlp = None
        else:
            print("spaCy not installed. Using basic NLP processing.")
            self.use_spacy = False
            self.nlp = None
        
        # Define intent patterns and entities
        self.intent_patterns = {
            'search_product': [
                r'find|search|look for|show me|get me|i want|i need|looking for',
                r'products?|items?|things?|stuff|shoes|mobile|phone|laptop|clothes|dress|shirt'
            ],
            'add_to_cart': [
                r'add.*cart|put.*cart|cart.*add|buy this|purchase this|take this',
                r'item \d+|product \d+|\d+.*item|\d+.*product'
            ],
            'view_cart': [
                r'show.*cart|view.*cart|my cart|what.*cart|cart.*contents|in.*cart'
            ],
            'product_details': [
                r'tell me about|describe|details of|information about|specs of|more about',
                r'item \d+|product \d+|\d+.*item|\d+.*product|this.*item|this.*product'
            ],
            'compare_products': [
                r'compare|difference|which.*better|versus|vs\.|against'
            ],
            'checkout': [
                r'checkout|proceed|buy now|purchase|order|complete.*order'
            ],
            'help': [
                r'help|what.*do|how.*work|commands|options|guide'
            ],
            'navigation': [
                r'next|previous|back|forward|first|last|page \d+'
            ]
        }
        
        # Product categories and synonyms
        self.category_synonyms = {
            'footwear': ['shoes', 'sneakers', 'boots', 'sandals', 'slippers', 'heels', 'flats', 'loafers', 'footwear'],
            'clothing': ['clothes', 'dress', 'shirt', 'pant', 'jeans', 'top', 'kurta', 'saree', 'blouse', 'jacket'],
            'electronics': ['phone', 'mobile', 'laptop', 'computer', 'headphones', 'speaker', 'tablet', 'gadget'],
            'books': ['book', 'novel', 'textbook', 'guide', 'manual', 'magazine', 'journal'],
            'home': ['furniture', 'chair', 'table', 'bed', 'sofa', 'lamp', 'decor', 'cushion', 'curtain'],
            'beauty': ['makeup', 'cosmetics', 'cream', 'lotion', 'perfume', 'shampoo', 'skincare']
        }
        
        # Color patterns
        self.colors = [
            'red', 'blue', 'green', 'yellow', 'black', 'white', 'brown', 'pink', 'purple', 'orange',
            'grey', 'gray', 'silver', 'gold', 'navy', 'maroon', 'beige', 'cream', 'tan', 'cyan'
        ]
        
        # Size patterns
        self.sizes = [
            'xs', 'small', 'medium', 'large', 'xl', 'xxl', 'xxxl',
            's', 'm', 'l', 'xl', '2xl', '3xl',
            r'\d+', r'size \d+', r'\d+ inch', r'\d+ cm'
        ]
        
        # Brand patterns (common Indian and international brands)
        self.brands = [
            'nike', 'adidas', 'puma', 'reebok', 'levis', 'samsung', 'apple', 'oneplus',
            'xiaomi', 'sony', 'lg', 'dell', 'hp', 'lenovo', 'asus', 'acer',
            'zara', 'h&m', 'uniqlo', 'forever21', 'myntra', 'biba', 'fabindia'
        ]
        
        # Price expressions
        self.price_patterns = {
            'under': r'under|below|less than|cheaper than|within|upto|up to',
            'above': r'above|over|more than|expensive than|starting from|minimum',
            'between': r'between|from.*to|range.*to|\d+.*to.*\d+',
            'exact': r'exactly|precisely|just|around|approximately|about'
        }
    
    def parse_user_input(self, text: str) -> Dict[str, Any]:
        """
        Main function to parse user input and extract intents and entities
        Returns comprehensive analysis of user's request
        """
        text = text.lower().strip()
        
        result = {
            'original_text': text,
            'intent': self._detect_intent(text),
            'entities': self._extract_entities(text),
            'confidence': 0.0,
            'suggestions': [],
            'clarifications_needed': []
        }
        
        # Calculate confidence based on pattern matches
        result['confidence'] = self._calculate_confidence(text, result['intent'])
        
        # Generate suggestions for ambiguous queries
        if result['confidence'] < 0.7:
            result['suggestions'] = self._generate_suggestions(text, result)
        
        # Identify if clarifications are needed
        result['clarifications_needed'] = self._identify_clarifications(result)
        
        return result
    
    def _detect_intent(self, text: str) -> str:
        """Detect the primary intent of the user's input"""
        intent_scores = defaultdict(int)
        
        # Check for product category keywords first - strong indicator of search intent
        product_keywords = ['shoes', 'mobile', 'phone', 'laptop', 'clothes', 'dress', 'shirt', 'jeans', 'book', 'furniture', 'makeup']
        has_product_keyword = any(keyword in text for keyword in product_keywords)
        
        # Check for search indicators
        search_indicators = ['find', 'search', 'look for', 'show me', 'get me', 'i want', 'i need']
        has_search_indicator = any(indicator in text for indicator in search_indicators)
        
        # If we have product keywords or search indicators, prioritize search
        if has_product_keyword or has_search_indicator:
            intent_scores['search_product'] += 3
        
        # Check all patterns
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    intent_scores[intent] += 1
        
        # Special case handling for numbers with items/products
        if any(word in text for word in ['item', 'product']) and any(char.isdigit() for char in text):
            if 'add' in text or 'cart' in text:
                return 'add_to_cart'
            elif 'tell' in text or 'about' in text or 'detail' in text:
                return 'product_details'
        
        # Return highest scoring intent
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        
        # Default to search if no clear intent but mentions products
        if has_product_keyword:
            return 'search_product'
        
        # Final fallback
        return 'search_product'
    
    def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract various entities from the text"""
        entities = {
            'product_category': None,
            'brand': None,
            'color': None,
            'size': None,
            'price_range': None,
            'item_number': None,
            'keywords': [],
            'modifiers': []
        }
        
        # Extract product category
        for category, synonyms in self.category_synonyms.items():
            if any(synonym in text for synonym in synonyms):
                entities['product_category'] = category
                break
        
        # Extract brand
        for brand in self.brands:
            if brand in text:
                entities['brand'] = brand
                break
        
        # Extract color
        for color in self.colors:
            if color in text:
                entities['color'] = color
                break
        
        # Extract size
        for size_pattern in self.sizes:
            if re.search(size_pattern, text, re.IGNORECASE):
                entities['size'] = re.search(size_pattern, text, re.IGNORECASE).group()
                break
        
        # Extract price range
        entities['price_range'] = self._extract_price_range(text)
        
        # Extract item number
        item_match = re.search(r'item\s*(\d+)|product\s*(\d+)|(\d+)\s*item|(\d+)\s*product', text)
        if item_match:
            entities['item_number'] = int([g for g in item_match.groups() if g][0])
        
        # Extract keywords (meaningful words)
        if self.use_spacy and self.nlp:
            doc = self.nlp(text)
            entities['keywords'] = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha and len(token.text) > 2]
        else:
            # Basic keyword extraction
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'this', 'that', 'i', 'you', 'me', 'my', 'your', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'can', 'may', 'might'}
            words = re.findall(r'\b\w+\b', text.lower())
            entities['keywords'] = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Extract modifiers (adjectives that describe the product)
        modifiers = []
        modifier_patterns = [
            r'cheap|expensive|affordable|premium|luxury|high-quality|best|good|excellent|top',
            r'new|latest|old|vintage|classic|modern|trendy|stylish|fashionable',
            r'comfortable|durable|lightweight|heavy|soft|hard|waterproof|breathable'
        ]
        
        for pattern in modifier_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            modifiers.extend(matches)
        
        entities['modifiers'] = list(set(modifiers))
        
        return entities
    
    def _extract_price_range(self, text: str) -> Dict[str, int]:
        """Extract price range information from text"""
        price_info = {'min_price': None, 'max_price': None, 'type': None}
        
        # Extract numeric values that could be prices
        numbers = re.findall(r'\d+(?:,\d+)*', text)
        prices = [int(num.replace(',', '')) for num in numbers if int(num.replace(',', '')) > 10]
        
        if not prices:
            return price_info
        
        # Determine price constraint type
        for price_type, pattern in self.price_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                price_info['type'] = price_type
                break
        
        # Apply constraints based on type
        if price_info['type'] == 'under':
            price_info['max_price'] = max(prices)
        elif price_info['type'] == 'above':
            price_info['min_price'] = min(prices)
        elif price_info['type'] == 'between' and len(prices) >= 2:
            price_info['min_price'] = min(prices)
            price_info['max_price'] = max(prices)
        elif price_info['type'] == 'exact':
            # For "around X", set a range of ±20%
            target_price = prices[0]
            price_info['min_price'] = int(target_price * 0.8)
            price_info['max_price'] = int(target_price * 1.2)
        else:
            # Default: treat as maximum price
            price_info['max_price'] = max(prices)
        
        return price_info
    
    def _calculate_confidence(self, text: str, intent: str) -> float:
        """Calculate confidence score for the detected intent"""
        if not intent:
            return 0.0
        
        patterns = self.intent_patterns.get(intent, [])
        matches = sum(1 for pattern in patterns if re.search(pattern, text, re.IGNORECASE))
        
        # Base confidence from pattern matches
        confidence = min(matches / len(patterns), 1.0) if patterns else 0.5
        
        # Boost confidence for clear indicators
        if intent == 'search_product' and any(cat in text for cats in self.category_synonyms.values() for cat in cats):
            confidence += 0.2
        
        if intent == 'add_to_cart' and re.search(r'item\s*\d+|product\s*\d+', text):
            confidence += 0.3
        
        if intent == 'product_details' and re.search(r'item\s*\d+|product\s*\d+', text):
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _generate_suggestions(self, text: str, analysis: Dict) -> List[str]:
        """Generate suggestions for ambiguous or low-confidence queries"""
        suggestions = []
        
        if analysis['confidence'] < 0.5:
            suggestions.append("Could you please be more specific about what you're looking for?")
        
        if not analysis['entities']['product_category']:
            suggestions.append("What type of product are you interested in? (e.g., shoes, clothes, electronics)")
        
        if analysis['intent'] == 'search_product' and not analysis['entities']['keywords']:
            suggestions.append("Please specify the product name or category you want to search for.")
        
        if 'add' in text and 'cart' in text and not analysis['entities']['item_number']:
            suggestions.append("Which item would you like to add to cart? Please specify the item number.")
        
        return suggestions
    
    def _identify_clarifications(self, analysis: Dict) -> List[str]:
        """Identify what clarifications might be needed"""
        clarifications = []
        
        entities = analysis['entities']
        
        if analysis['intent'] == 'search_product':
            if not entities['product_category'] and not entities['keywords']:
                clarifications.append('product_type')
            
            if entities['price_range']['type'] == 'between' and (
                not entities['price_range']['min_price'] or not entities['price_range']['max_price']
            ):
                clarifications.append('price_range')
        
        if analysis['intent'] in ['add_to_cart', 'product_details'] and not entities['item_number']:
            clarifications.append('item_number')
        
        return clarifications
    
    def format_search_query(self, analysis: Dict) -> Dict[str, Any]:
        """Format the analysis into a search query"""
        entities = analysis['entities']
        
        # Build search keywords more intelligently
        keywords = []
        
        # Prioritize product category
        if entities['product_category']:
            keywords.append(entities['product_category'])
        
        # Add brand if specified
        if entities['brand']:
            keywords.append(entities['brand'])
        
        # Add color if specified
        if entities['color']:
            keywords.append(entities['color'])
        
        # Add modifiers (adjectives)
        if entities['modifiers']:
            keywords.extend(entities['modifiers'])
        
        # Add relevant keywords, filtering out common words
        if entities['keywords']:
            # Filter out search verbs and common words
            filtered_keywords = []
            skip_words = {'find', 'search', 'show', 'get', 'want', 'need', 'under', 'above', 'rupees', 'rs', 'price', 'range'}
            for keyword in entities['keywords']:
                if keyword.lower() not in skip_words and len(keyword) > 2:
                    filtered_keywords.append(keyword)
            keywords.extend(filtered_keywords[:3])  # Limit to avoid noise
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword.lower() not in seen:
                seen.add(keyword.lower())
                unique_keywords.append(keyword)
        
        # If no specific keywords, try to extract from original text
        if not unique_keywords:
            original_text = analysis.get('original_text', '')
            # Look for product mentions
            product_mentions = []
            for category, synonyms in self.category_synonyms.items():
                for synonym in synonyms:
                    if synonym in original_text.lower():
                        product_mentions.append(synonym)
                        break
            if product_mentions:
                unique_keywords.extend(product_mentions[:2])
        
        query = {
            'keywords': ' '.join(unique_keywords) if unique_keywords else 'products',
            'min_price': entities['price_range']['min_price'],
            'max_price': entities['price_range']['max_price'],
            'category': entities['product_category'],
            'brand': entities['brand'],
            'color': entities['color'],
            'size': entities['size'],
            'item_number': entities['item_number']
        }
        
        return query
    
    def generate_voice_response(self, analysis: Dict, context: str = "search") -> str:
        """Generate natural voice responses based on analysis"""
        entities = analysis['entities']
        intent = analysis['intent']
        
        if analysis['confidence'] < 0.5:
            return "I'm not sure I understood that correctly. " + "; ".join(analysis['suggestions'])
        
        if intent == 'search_product':
            response = "I'll search for "
            
            if entities['modifiers']:
                response += " ".join(entities['modifiers']) + " "
            
            if entities['color']:
                response += entities['color'] + " "
            
            if entities['brand']:
                response += entities['brand'] + " "
            
            if entities['product_category']:
                response += entities['product_category']
            elif entities['keywords']:
                response += " ".join(entities['keywords'][:3])  # Limit to first 3 keywords
            else:
                response += "products"
            
            if entities['price_range']['max_price']:
                response += f" under rupees {entities['price_range']['max_price']}"
            elif entities['price_range']['min_price']:
                response += f" starting from rupees {entities['price_range']['min_price']}"
            
            response += ". Please wait while I find the best options for you from multiple stores."
            
        elif intent == 'add_to_cart':
            if entities['item_number']:
                response = f"I'll add item {entities['item_number']} to your cart."
            else:
                response = "Which item would you like to add to your cart? Please specify the item number."
        
        elif intent == 'product_details':
            if entities['item_number']:
                response = f"Here are the details for item {entities['item_number']}:"
            else:
                response = "Which product would you like to know more about? Please specify the item number."
        
        elif intent == 'view_cart':
            response = "Here's what's currently in your shopping cart:"
        
        elif intent == 'compare_products':
            response = "I'll compare the products for you based on price, features, and ratings."
        
        elif intent == 'checkout':
            response = "I'll help you proceed to checkout with your current cart items."
        
        elif intent == 'help':
            response = "I can help you search for products, add items to cart, view product details, and more. What would you like to do?"
        
        else:
            response = "I understand you want to " + intent.replace('_', ' ') + ". Let me help you with that."
        
        return response
