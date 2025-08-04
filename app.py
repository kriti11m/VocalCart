import json
import logging
from voice_input import get_voice_input
from voice_output import speak
from query_parser import parse_query
from command_parser import parse_command
from flipkart_scraper import search_flipkart
from shopping_cart import ShoppingCart
from product_description import describe_product, compare_products, generate_product_summary

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceShoppingApp:
    def __init__(self):
        self.cart = ShoppingCart()
        self.current_products = []
        self.session_active = True
        
    def start(self):
        speak("Welcome to VocalCart! Your voice-powered shopping assistant.")
        speak("You can search for products, add items to cart, or ask for help.")
        
        while self.session_active:
            try:
                self.handle_user_input()
            except KeyboardInterrupt:
                self.exit_app()
            except Exception as e:
                logger.error(f"Error: {e}")
                speak("Sorry, I encountered an error. Please try again.")
    
    def handle_user_input(self):
        speak("What would you like to do?")
        query = get_voice_input()
        
        if not query:
            speak("I didn't catch that. Please try again.")
            return
            
        # Parse command first
        command_type, command_data = parse_command(query)
        
        if command_type == "search":
            self.handle_search(query)
        elif command_type == "add_to_cart":
            self.handle_add_to_cart(command_data)
        elif command_type == "view_cart":
            self.handle_view_cart()
        elif command_type == "remove_from_cart":
            self.handle_remove_from_cart(command_data)
        elif command_type == "product_details":
            self.handle_product_details(command_data)
        elif command_type == "compare":
            self.handle_compare_products(command_data)
        elif command_type == "checkout":
            self.handle_checkout()
        elif command_type == "help":
            self.show_help()
        elif command_type == "exit":
            self.exit_app()
        else:
            self.handle_search(query)  # Default to search
    
    def handle_search(self, query):
        speak("Searching for products...")
        keywords, min_price, max_price = parse_query(query)
        
        try:
            products = search_flipkart(keywords, min_price, max_price)
            self.current_products = products[:10]  # Store top 10
            
            if not products:
                speak("Sorry, I couldn't find any products matching your search.")
                return
                
            # Use the new summary function
            summary = generate_product_summary(self.current_products)
            speak(summary)
            
            speak("Here are the top options:")
            for i, product in enumerate(self.current_products[:5]):
                title = product['title'][:50]  # Truncate long titles
                price = product['price']
                speak(f"Option {i+1}: {title} for rupees {price}")
                
            speak("Would you like to hear more options, get details about a specific item, or add something to your cart?")
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            speak("Sorry, I'm having trouble searching right now. Please try again.")
    
    def handle_add_to_cart(self, item_data):
        try:
            item_number = item_data.get('item_number', 1) - 1
            quantity = item_data.get('quantity', 1)
            
            if 0 <= item_number < len(self.current_products):
                product = self.current_products[item_number]
                self.cart.add_item(product, quantity)
                title = product['title'][:30]  # Truncate for speech
                speak(f"Added {quantity} {title} to your cart for rupees {product['price']} each.")
            else:
                speak("Please specify a valid item number from the search results.")
                
        except Exception as e:
            logger.error(f"Add to cart error: {e}")
            speak("Sorry, I couldn't add that item to your cart.")
    
    def handle_view_cart(self):
        items = self.cart.get_items()
        if not items:
            speak("Your cart is empty.")
            return
            
        speak(f"You have {len(items)} items in your cart:")
        total = 0
        
        for i, item in enumerate(items, 1):
            item_total = item['price'] * item['quantity']
            total += item_total
            title = item['title'][:30]  # Truncate for speech
            speak(f"Item {i}: {item['quantity']} {title} for rupees {item_total}")
            
        speak(f"Your total is rupees {total}. Would you like to checkout or continue shopping?")
    
    def handle_remove_from_cart(self, item_data):
        speak("To remove items, say 'remove item 1' or similar. This feature is coming soon!")
    
    def handle_product_details(self, item_data):
        try:
            item_number = item_data.get('item_number', 1) - 1
            if 0 <= item_number < len(self.current_products):
                product = self.current_products[item_number]
                description = describe_product(product)
                speak(description)
            else:
                speak("Please specify a valid item number from the current search results.")
        except Exception as e:
            logger.error(f"Product details error: {e}")
            speak("Sorry, I couldn't get the product details.")
    
    def handle_compare_products(self, item_data):
        if len(self.current_products) < 2:
            speak("I need at least 2 products to compare. Please search for products first.")
            return
            
        try:
            # Compare top 3 products by default
            products_to_compare = self.current_products[:3]
            comparison = compare_products(products_to_compare)
            speak(comparison)
        except Exception as e:
            logger.error(f"Comparison error: {e}")
            speak("Sorry, I couldn't compare the products.")
    
    def handle_checkout(self):
        items = self.cart.get_items()
        if not items:
            speak("Your cart is empty. Add some items first!")
            return
            
        total = sum(item['price'] * item['quantity'] for item in items)
        speak(f"Your order total is rupees {total}. Proceeding to checkout...")
        speak("This is a demo. In a real app, you would be redirected to payment.")
        speak("Thank you for shopping with VocalCart!")
    
    def show_help(self):
        help_text = """
        Here are some commands you can try:
        Search for products by saying: search for shoes under 2000 rupees.
        Add items by saying: add item 1 to cart.
        View your cart by saying: show my cart.
        Get product details by saying: tell me about item 2.
        Compare products by saying: compare products.
        Checkout by saying: checkout.
        Exit by saying: exit or goodbye.
        """
        speak(help_text)
    
    def exit_app(self):
        speak("Thank you for using VocalCart! Goodbye!")
        self.session_active = False

if __name__ == "__main__":
    app = VoiceShoppingApp()
    app.start()
