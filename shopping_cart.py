import json
import os
import logging
from datetime import datetime
from product_description import format_price_for_voice, clean_title_for_voice

# Configure logging
logger = logging.getLogger(__name__)

class ShoppingCart:
    def __init__(self, cart_file='cart.json'):
        self.cart_file = cart_file
        self.cart = self.load_cart()
        
    def get_items(self):
        """Get all items in the cart"""
        return self.cart.get('items', [])
    
    def load_cart(self):
        """Load cart from file or create empty cart"""
        if os.path.exists(self.cart_file):
            try:
                with open(self.cart_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cart file {self.cart_file}: {e}")
                return {'items': [], 'total': 0, 'created': datetime.now().isoformat()}
        return {'items': [], 'total': 0, 'created': datetime.now().isoformat()}
    
    def save_cart(self):
        """Save cart to file"""
        try:
            # Create directory if it doesn't exist
            cart_dir = os.path.dirname(self.cart_file)
            if cart_dir and not os.path.exists(cart_dir):
                os.makedirs(cart_dir)
                
            with open(self.cart_file, 'w') as f:
                json.dump(self.cart, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cart to {self.cart_file}: {e}")
    
    def add_item(self, product):
        """Add a product to the cart"""
        if not product:
            return False, "No product to add"
        
        # Check if item already exists
        for item in self.cart['items']:
            if item.get('title') == product.get('title'):
                item['quantity'] = item.get('quantity', 1) + 1
                self.update_total()
                self.save_cart()
                return True, f"Increased quantity of {clean_title_for_voice(product.get('title', 'item'))} to {item['quantity']}"
        
        # Add new item
        cart_item = {
            'title': product.get('title', 'Unknown item'),
            'price': product.get('price', 0),
            'quantity': 1,
            'added_at': datetime.now().isoformat()
        }
        
        self.cart['items'].append(cart_item)
        self.update_total()
        self.save_cart()
        
        return True, f"Added {clean_title_for_voice(product.get('title', 'item'))} to your cart"
    
    def remove_item(self, product_title=None, index=None):
        """Remove an item from cart by title or index"""
        if not self.cart['items']:
            return False, "Your cart is empty"
        
        if index is not None:
            if 1 <= index <= len(self.cart['items']):
                removed_item = self.cart['items'].pop(index - 1)
                self.update_total()
                self.save_cart()
                return True, f"Removed {clean_title_for_voice(removed_item['title'])} from your cart"
            else:
                return False, f"Invalid item number. Please choose between 1 and {len(self.cart['items'])}"
        
        if product_title:
            for i, item in enumerate(self.cart['items']):
                if product_title.lower() in item['title'].lower():
                    removed_item = self.cart['items'].pop(i)
                    self.update_total()
                    self.save_cart()
                    return True, f"Removed {clean_title_for_voice(removed_item['title'])} from your cart"
            
            return False, f"Could not find {product_title} in your cart"
        
        return False, "Please specify which item to remove"
    
    def update_total(self):
        """Update cart total"""
        total = 0
        for item in self.cart['items']:
            price = item.get('price', 0)
            quantity = item.get('quantity', 1)
            
            # Handle price as string
            if isinstance(price, str):
                import re
                price_match = re.search(r'[\d,]+', price)
                if price_match:
                    price = int(price_match.group().replace(',', ''))
                else:
                    price = 0
            
            total += price * quantity
        
        self.cart['total'] = total
    
    def get_cart_summary(self):
        """Get a voice-friendly cart summary"""
        if not self.cart['items']:
            return "Your cart is empty"
        
        item_count = len(self.cart['items'])
        total_quantity = sum(item.get('quantity', 1) for item in self.cart['items'])
        
        summary_parts = [
            f"You have {total_quantity} item{'s' if total_quantity != 1 else ''} in your cart"
        ]
        
        for i, item in enumerate(self.cart['items'], 1):
            title = clean_title_for_voice(item['title'])
            price = format_price_for_voice(item['price'])
            quantity = item.get('quantity', 1)
            
            if quantity > 1:
                summary_parts.append(f"Item {i}: {quantity} units of {title} at {price} each")
            else:
                summary_parts.append(f"Item {i}: {title} at {price}")
        
        total_price = format_price_for_voice(self.cart['total'])
        summary_parts.append(f"Total amount: {total_price}")
        
        return ". ".join(summary_parts) + "."
    
    def clear_cart(self):
        """Clear all items from cart"""
        self.cart = {'items': [], 'total': 0, 'created': datetime.now().isoformat()}
        self.save_cart()
        return "Your cart has been cleared"
    
    def get_item_count(self):
        """Get total number of items in cart"""
        return len(self.cart['items'])
    
    def get_total_amount(self):
        """Get total cart amount"""
        return self.cart['total']
    
    def proceed_to_checkout(self):
        """Generate checkout summary"""
        if not self.cart['items']:
            return False, "Your cart is empty. Add some items before checkout."
        
        checkout_summary = [
            "Proceeding to checkout.",
            self.get_cart_summary(),
            "To complete your purchase, you would typically be redirected to a payment gateway.",
            "For this demo, your order has been placed successfully!",
            "Thank you for using VocalCart!"
        ]
        
        # Clear cart after successful checkout
        self.clear_cart()
        
        return True, " ".join(checkout_summary)
