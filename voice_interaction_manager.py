import json
import logging
from typing import Dict, List, Any, Optional
import re
from advanced_nlp_engine import AdvancedNLPEngine
from accessibility_features import AccessibleProductDescriber
from enhanced_product_database import EnhancedProductDatabase

class VoiceInteractionManager:
    """
    Comprehensive Voice Interaction Manager for VocalCart
    Implements the complete voice-based shopping experience as per system architecture
    Designed specifically for visually impaired users with full accessibility support
    """
    
    def __init__(self):
        self.nlp_engine = AdvancedNLPEngine()
        self.accessibility_describer = AccessibleProductDescriber()
        self.enhanced_db = EnhancedProductDatabase()
        
        # Session state management
        self.session_state = {
            'current_products': [],
            'current_page': 0,
            'items_per_page': 5,  # Smaller pages for better voice navigation
            'last_query': '',
            'conversation_context': [],
            'user_preferences': {},
            'shopping_cart': [],
            'current_product_focus': None,
            'navigation_history': []
        }
        
        # Voice interaction patterns
        self.voice_commands = {
            'navigation': {
                'next': ['next', 'next item', 'next product', 'continue', 'forward'],
                'previous': ['previous', 'prev', 'back', 'go back', 'last item'],
                'repeat': ['repeat', 'say again', 'repeat that', 'say that again'],
                'first': ['first', 'first item', 'go to first', 'start'],
                'last': ['last', 'last item', 'go to last', 'end']
            },
            'actions': {
                'add_to_cart': ['add to cart', 'buy this', 'purchase this', 'take this', 'add this'],
                'more_details': ['more details', 'tell me more', 'more info', 'detailed info', 'specifications'],
                'compare': ['compare', 'compare with', 'versus', 'difference', 'which is better'],
                'skip': ['skip', 'skip this', 'next option', 'not interested'],
                'bookmark': ['bookmark', 'save this', 'remember this', 'add to wishlist']
            },
            'search_refinement': {
                'cheaper': ['cheaper', 'less expensive', 'lower price', 'budget option'],
                'expensive': ['more expensive', 'premium', 'luxury', 'high end'],
                'different_color': ['different color', 'other colors', 'color options'],
                'different_brand': ['different brand', 'other brands', 'alternative brands'],
                'similar': ['similar', 'like this', 'similar products', 'comparable items']
            }
        }
        
        # Accessibility features
        self.accessibility_settings = {
            'speech_rate': 'normal',  # slow, normal, fast
            'detail_level': 'comprehensive',  # brief, standard, comprehensive
            'price_context': True,  # Include price comparisons
            'navigation_hints': True,  # Provide navigation instructions
            'confirmation_prompts': True,  # Ask for confirmation on actions
            'reading_order': 'structured'  # structured, sequential
        }
    
    def process_voice_command(self, voice_input: str, session_id: str = 'default') -> Dict[str, Any]:
        """
        Main function to process voice commands and return appropriate responses
        Implements the complete voice interaction flow
        """
        # Clean and normalize input
        normalized_input = self._normalize_voice_input(voice_input)
        
        # Use NLP engine to analyze input
        analysis = self.nlp_engine.parse_user_input(normalized_input)
        
        # Update conversation context
        self._update_conversation_context(normalized_input, analysis)
        
        # Process based on intent
        intent = analysis['intent']
        
        if intent == 'search_product':
            return self._handle_product_search(analysis, normalized_input)
        elif intent == 'navigation':
            return self._handle_navigation(analysis, normalized_input)
        elif intent == 'product_details':
            return self._handle_product_details(analysis, normalized_input)
        elif intent == 'add_to_cart':
            return self._handle_add_to_cart(analysis, normalized_input)
        elif intent == 'view_cart':
            return self._handle_view_cart()
        elif intent == 'compare_products':
            return self._handle_product_comparison(analysis)
        elif intent == 'checkout':
            return self._handle_checkout()
        elif intent == 'help':
            return self._handle_help_request(analysis)
        else:
            return self._handle_general_query(analysis, normalized_input)
    
    def _normalize_voice_input(self, voice_input: str) -> str:
        """Normalize voice input for better processing"""
        # Convert to lowercase
        normalized = voice_input.lower().strip()
        
        # Handle common voice recognition errors
        corrections = {
            'rupeas': 'rupees',
            'rupes': 'rupees',
            'under rupees': 'under',
            'add too cart': 'add to cart',
            'ad to cart': 'add to cart',
            'tel me': 'tell me',
            'show mee': 'show me',
            'produck': 'product',
            'itam': 'item',
            'shoos': 'shoes',
            'mobil': 'mobile'
        }
        
        for wrong, correct in corrections.items():
            normalized = normalized.replace(wrong, correct)
        
        return normalized
    
    def _handle_product_search(self, analysis: Dict, voice_input: str) -> Dict[str, Any]:
        """Handle product search requests with voice-optimized responses"""
        query_data = self.nlp_engine.format_search_query(analysis)
        
        # Generate voice response for search initiation
        search_response = self.nlp_engine.generate_voice_response(analysis, "search")
        
        # Store query for context
        self.session_state['last_query'] = query_data['keywords']
        self.session_state['current_page'] = 0
        
        return {
            'action': 'search',
            'message': search_response,
            'query_data': query_data,
            'voice_optimized': True,
            'accessibility_features': {
                'provide_overview': True,
                'detailed_descriptions': True,
                'navigation_instructions': True
            }
        }
    
    def _handle_navigation(self, analysis: Dict, voice_input: str) -> Dict[str, Any]:
        """Handle navigation commands with accessibility support"""
        current_products = self.session_state['current_products']
        current_page = self.session_state['current_page']
        items_per_page = self.session_state['items_per_page']
        
        navigation_type = self._detect_navigation_type(voice_input)
        
        if navigation_type == 'next':
            if (current_page + 1) * items_per_page < len(current_products):
                self.session_state['current_page'] += 1
                new_page = self.session_state['current_page']
                response = f"Moving to page {new_page + 1}. Here are the next products:"
            else:
                response = "You're already viewing the last page of results. Would you like to start a new search?"
        
        elif navigation_type == 'previous':
            if current_page > 0:
                self.session_state['current_page'] -= 1
                new_page = self.session_state['current_page']
                response = f"Going back to page {new_page + 1}. Here are the previous products:"
            else:
                response = "You're already on the first page. These are the first products from your search."
        
        elif navigation_type == 'repeat':
            response = "Let me repeat the current products for you:"
        
        elif navigation_type == 'first':
            self.session_state['current_page'] = 0
            response = "Going to the first page. Here are the first products:"
        
        elif navigation_type == 'last':
            max_page = (len(current_products) - 1) // items_per_page
            self.session_state['current_page'] = max_page
            response = f"Going to the last page. Here are the final products:"
        
        else:
            response = "I didn't understand that navigation command. You can say 'next', 'previous', 'first', or 'last'."
        
        return {
            'action': 'navigation',
            'message': response,
            'current_page': self.session_state['current_page'],
            'products_to_read': self._get_current_page_products(),
            'navigation_context': self._get_navigation_context()
        }
    
    def _handle_product_details(self, analysis: Dict, voice_input: str) -> Dict[str, Any]:
        """Handle requests for detailed product information"""
        entities = analysis['entities']
        item_number = entities.get('item_number')
        
        if not item_number:
            # Try to extract from current context or ask for clarification
            if self.session_state['current_product_focus']:
                item_number = self.session_state['current_product_focus']
            else:
                return {
                    'action': 'clarification',
                    'message': "Which product would you like to know more about? Please say the item number, for example, 'tell me about item 1'.",
                    'suggestions': ["Tell me about item 1", "More details about product 2", "Describe item 3"]
                }
        
        current_products = self.session_state['current_products']
        
        if 1 <= item_number <= len(current_products):
            product = current_products[item_number - 1]
            
            # Generate comprehensive description
            detailed_description = self.accessibility_describer.describe_product_for_accessibility(
                product, position=item_number
            )
            
            # Store current focus for context
            self.session_state['current_product_focus'] = item_number
            
            return {
                'action': 'product_details',
                'message': detailed_description,
                'product': product,
                'item_number': item_number,
                'follow_up_suggestions': [
                    f"Add item {item_number} to cart",
                    f"Compare item {item_number} with others",
                    "Tell me about the next item",
                    "Go back to search results"
                ]
            }
        else:
            return {
                'action': 'error',
                'message': f"I couldn't find item {item_number}. I have {len(current_products)} products available. Please choose a number between 1 and {len(current_products)}."
            }
    
    def _handle_add_to_cart(self, analysis: Dict, voice_input: str) -> Dict[str, Any]:
        """Handle add to cart requests with confirmation"""
        entities = analysis['entities']
        item_number = entities.get('item_number')
        
        if not item_number and self.session_state['current_product_focus']:
            item_number = self.session_state['current_product_focus']
        
        if not item_number:
            return {
                'action': 'clarification',
                'message': "Which item would you like to add to your cart? Please specify the item number, like 'add item 1 to cart'.",
                'suggestions': ["Add item 1 to cart", "Add product 2", "Put item 3 in cart"]
            }
        
        current_products = self.session_state['current_products']
        
        if 1 <= item_number <= len(current_products):
            product = current_products[item_number - 1]
            
            # Add to cart
            self.session_state['shopping_cart'].append({
                'product': product,
                'quantity': 1,
                'added_at': 'now'  # In real implementation, use proper timestamp
            })
            
            # Generate confirmation message
            product_title = product.get('title', 'Unknown product')
            product_price = product.get('price', 'Price not available')
            
            if self.accessibility_settings['confirmation_prompts']:
                message = f"I've added {product_title} priced at rupees {product_price} to your cart. You now have {len(self.session_state['shopping_cart'])} items in your cart. Would you like to continue shopping or view your cart?"
            else:
                message = f"Added {product_title} to cart. Cart total: {len(self.session_state['shopping_cart'])} items."
            
            return {
                'action': 'add_to_cart',
                'message': message,
                'product': product,
                'cart_count': len(self.session_state['shopping_cart']),
                'suggestions': [
                    "Continue shopping",
                    "View my cart",
                    "Tell me about the next item",
                    "Proceed to checkout"
                ]
            }
        else:
            return {
                'action': 'error',
                'message': f"I couldn't find item {item_number}. Please choose a valid item number from the current search results."
            }
    
    def _handle_view_cart(self) -> Dict[str, Any]:
        """Handle cart viewing with detailed voice description"""
        cart_items = self.session_state['shopping_cart']
        
        if not cart_items:
            return {
                'action': 'view_cart',
                'message': "Your shopping cart is currently empty. Would you like to search for products to add?",
                'cart_items': [],
                'total_amount': 0,
                'suggestions': ["Search for products", "Find shoes", "Look for electronics"]
            }
        
        # Calculate total
        total_amount = 0
        cart_descriptions = []
        
        for i, cart_item in enumerate(cart_items, 1):
            product = cart_item['product']
            quantity = cart_item.get('quantity', 1)
            price = product.get('price', 0)
            
            if isinstance(price, str):
                price = int(''.join(filter(str.isdigit, price)) or 0)
            
            total_amount += price * quantity
            
            item_description = f"Item {i}: {product.get('title', 'Unknown product')}, priced at rupees {price}"
            if quantity > 1:
                item_description += f", quantity {quantity}"
            
            cart_descriptions.append(item_description)
        
        # Generate comprehensive cart summary
        message = f"You have {len(cart_items)} items in your cart. "
        message += ". ".join(cart_descriptions)
        message += f". Your total cart value is rupees {total_amount}. "
        message += "You can proceed to checkout, continue shopping, or remove items from your cart."
        
        return {
            'action': 'view_cart',
            'message': message,
            'cart_items': cart_items,
            'total_amount': total_amount,
            'item_count': len(cart_items),
            'suggestions': [
                "Proceed to checkout",
                "Continue shopping",
                "Remove an item",
                "Search for more products"
            ]
        }
    
    def _handle_product_comparison(self, analysis: Dict) -> Dict[str, Any]:
        """Handle product comparison requests"""
        current_products = self.session_state['current_products']
        
        if len(current_products) < 2:
            return {
                'action': 'error',
                'message': "I need at least 2 products to compare. Please search for products first, then ask me to compare them."
            }
        
        # Use first few products for comparison
        products_to_compare = current_products[:min(3, len(current_products))]
        
        comparison = self.accessibility_describer.create_comparison_for_accessibility(products_to_compare)
        
        return {
            'action': 'compare',
            'message': comparison,
            'compared_products': products_to_compare,
            'suggestions': [
                "Tell me more about the cheapest option",
                "Add the best rated item to cart",
                "Search for similar products",
                "Show me more expensive options"
            ]
        }
    
    def _handle_checkout(self) -> Dict[str, Any]:
        """Handle checkout process initiation"""
        cart_items = self.session_state['shopping_cart']
        
        if not cart_items:
            return {
                'action': 'error',
                'message': "Your cart is empty. Please add some items to your cart before proceeding to checkout."
            }
        
        total_amount = sum(
            item['product'].get('price', 0) * item.get('quantity', 1) 
            for item in cart_items
        )
        
        message = f"Proceeding to checkout with {len(cart_items)} items totaling rupees {total_amount}. "
        message += "Please note that this is a demo version. In a real application, you would be guided through address selection, payment options, and order confirmation with full voice support."
        
        return {
            'action': 'checkout',
            'message': message,
            'cart_summary': {
                'item_count': len(cart_items),
                'total_amount': total_amount,
                'items': cart_items
            },
            'next_steps': [
                "Select delivery address",
                "Choose payment method",
                "Review order details",
                "Confirm order"
            ]
        }
    
    def _handle_help_request(self, analysis: Dict) -> Dict[str, Any]:
        """Provide comprehensive help information"""
        help_message = """Welcome to VocalCart, your voice-controlled shopping assistant designed for accessibility. Here's what I can help you with:

        Search Commands:
        - "Find shoes under 2000 rupees"
        - "Search for Samsung mobile phones"
        - "Show me blue jeans"

        Navigation Commands:
        - "Next" - Move to next products
        - "Previous" - Go back to previous products
        - "Repeat" - Hear current products again

        Product Information:
        - "Tell me about item 1" - Get detailed product description
        - "More details about product 2" - Get specifications
        - "Compare products" - Compare multiple items

        Shopping Commands:
        - "Add item 1 to cart" - Add product to shopping cart
        - "Show my cart" - View cart contents
        - "Proceed to checkout" - Start checkout process

        All commands are designed to work naturally with voice input. I provide detailed descriptions including price context, store information, and accessibility features. What would you like to do?"""
        
        return {
            'action': 'help',
            'message': help_message,
            'command_categories': {
                'search': ['find', 'search', 'show me', 'look for'],
                'navigation': ['next', 'previous', 'repeat', 'first', 'last'],
                'details': ['tell me about', 'more details', 'describe'],
                'shopping': ['add to cart', 'show cart', 'checkout'],
                'comparison': ['compare', 'difference', 'which is better']
            }
        }
    
    def _handle_general_query(self, analysis: Dict, voice_input: str) -> Dict[str, Any]:
        """Handle general queries and provide helpful responses"""
        if analysis['confidence'] < 0.5:
            message = "I'm not sure I understood that correctly. " + " ".join(analysis['suggestions'])
            if not analysis['suggestions']:
                message += " Could you please rephrase your request? You can say things like 'find shoes', 'add item 1 to cart', or 'help' for more information."
        else:
            message = f"I understand you want to {analysis['intent'].replace('_', ' ')}. Let me help you with that."
        
        return {
            'action': 'general',
            'message': message,
            'suggestions': analysis.get('suggestions', []),
            'help_available': True
        }
    
    def _detect_navigation_type(self, voice_input: str) -> str:
        """Detect the type of navigation command"""
        voice_input = voice_input.lower()
        
        for nav_type, patterns in self.voice_commands['navigation'].items():
            if any(pattern in voice_input for pattern in patterns):
                return nav_type
        
        return 'unknown'
    
    def _get_current_page_products(self) -> List[Dict]:
        """Get products for the current page"""
        current_page = self.session_state['current_page']
        items_per_page = self.session_state['items_per_page']
        current_products = self.session_state['current_products']
        
        start_idx = current_page * items_per_page
        end_idx = start_idx + items_per_page
        
        return current_products[start_idx:end_idx]
    
    def _get_navigation_context(self) -> Dict[str, Any]:
        """Get navigation context information"""
        current_page = self.session_state['current_page']
        items_per_page = self.session_state['items_per_page']
        total_products = len(self.session_state['current_products'])
        total_pages = (total_products - 1) // items_per_page + 1 if total_products > 0 else 0
        
        return {
            'current_page': current_page + 1,
            'total_pages': total_pages,
            'total_products': total_products,
            'has_next': (current_page + 1) < total_pages,
            'has_previous': current_page > 0
        }
    
    def _update_conversation_context(self, voice_input: str, analysis: Dict) -> None:
        """Update conversation context for better understanding"""
        context_entry = {
            'input': voice_input,
            'intent': analysis['intent'],
            'entities': analysis['entities'],
            'timestamp': 'now'  # In real implementation, use proper timestamp
        }
        
        self.session_state['conversation_context'].append(context_entry)
        
        # Keep only last 10 interactions for context
        if len(self.session_state['conversation_context']) > 10:
            self.session_state['conversation_context'] = self.session_state['conversation_context'][-10:]
    
    def update_session_products(self, products: List[Dict]) -> None:
        """Update session with new product search results"""
        self.session_state['current_products'] = products
        self.session_state['current_page'] = 0
        self.session_state['current_product_focus'] = None
    
    def get_session_state(self) -> Dict[str, Any]:
        """Get current session state"""
        return self.session_state.copy()
    
    def reset_session(self) -> None:
        """Reset session state"""
        self.session_state = {
            'current_products': [],
            'current_page': 0,
            'items_per_page': 5,
            'last_query': '',
            'conversation_context': [],
            'user_preferences': {},
            'shopping_cart': [],
            'current_product_focus': None,
            'navigation_history': []
        }
