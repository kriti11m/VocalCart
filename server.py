from flask import Flask, render_template, request, jsonify, session
import json
from voice_input import get_voice_input
from voice_output import speak
from query_parser import parse_query
from command_parser import parse_command
from flipkart_scraper import search_flipkart
from multi_store_scraper import MultiStoreScraper
from accessibility_features import AccessibleProductDescriber
from enhanced_product_database import EnhancedProductDatabase
from voice_interaction_manager import VoiceInteractionManager
from shopping_cart import ShoppingCart
import logging

# Try to import product description functions, provide fallbacks if missing
try:
    from product_description import describe_product, compare_products, generate_product_summary
except ImportError:
    def describe_product(product):
        title = product.get('title', 'Unknown Product')
        price = product.get('price', 'Price not available')
        return f"This is {title}. It's priced at rupees {price}."
    
    def compare_products(products):
        return "Product comparison feature is not available."
    
    def generate_product_summary(products):
        return f"I found {len(products)} products for you."

app = Flask(__name__)
app.secret_key = 'vocalcart-secret-key-2025'
logging.basicConfig(level=logging.INFO)

# Initialize the accessibility features, enhanced database, and voice manager
# Skip web scraping for now due to ChromeDriver issues on macOS ARM64
accessibility_describer = AccessibleProductDescriber()
enhanced_db = EnhancedProductDatabase()
voice_manager = VoiceInteractionManager()

# Global storage for user sessions
user_sessions = {}

def get_user_cart():
    """Get or create cart for current session"""
    if 'user_id' not in session:
        session['user_id'] = 'user_' + str(hash(session.get('csrf_token', 'default')))
    
    user_id = session['user_id']
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'cart': ShoppingCart(),
            'current_products': []
        }
    return user_sessions[user_id]

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/voice-command', methods=['POST'])
def handle_voice_command():
    try:
        data = request.json
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({
                'action': 'error',
                'message': 'No command received. Please try speaking again.'
            })
        
        # Get user session for context
        user_session = get_user_cart()
        session_id = session.get('user_id', 'default')
        
        # Use comprehensive voice interaction manager
        voice_response = voice_manager.process_voice_command(command, session_id)
        
        # Handle different response types
        if voice_response['action'] == 'search':
            return handle_enhanced_search(voice_response, user_session)
        elif voice_response['action'] == 'navigation':
            return handle_voice_navigation(voice_response, user_session)
        elif voice_response['action'] == 'product_details':
            return jsonify(voice_response)
        elif voice_response['action'] == 'add_to_cart':
            return handle_voice_add_to_cart(voice_response, user_session)
        elif voice_response['action'] == 'view_cart':
            return handle_voice_view_cart(voice_response, user_session)
        elif voice_response['action'] == 'compare':
            return jsonify(voice_response)
        elif voice_response['action'] == 'checkout':
            return jsonify(voice_response)
        elif voice_response['action'] == 'help':
            return jsonify(voice_response)
        elif voice_response['action'] == 'clarification':
            return jsonify(voice_response)
        else:
            return jsonify(voice_response)
            
    except Exception as e:
        logging.error(f"Voice command error: {e}")
        return jsonify({
            'action': 'error',
            'message': 'Sorry, I encountered an error processing your voice command. Please try again.'
        }), 500

def handle_enhanced_search(voice_response, user_session):
    """Handle enhanced search with voice interaction manager"""
    try:
        query_data = voice_response.get('query_data', {})
        keywords = query_data.get('keywords', '')
        min_price = query_data.get('min_price')
        max_price = query_data.get('max_price')
        
        logging.info(f"Enhanced search for: '{keywords}' with price range: {min_price}-{max_price}")
        
        # Use enhanced database for reliable product search
        # (Web scraping disabled due to ChromeDriver compatibility issues on macOS ARM64)
        products = enhanced_db.search_products(keywords, min_price, max_price)
        scraping_successful = len(products) > 0
        
        # Mark products as from enhanced database
        for product in products:
            product['enhanced_db'] = True
        
        # Products are already available from enhanced database
        # No additional fallback needed
        
        # Update voice manager session
        voice_manager.update_session_products(products)
        
        # Store in user session for compatibility
        user_session['current_products'] = products[:15]
        
        # Generate accessibility summary
        search_summary = accessibility_describer.create_search_summary_for_accessibility(
            products[:15], keywords
        )
        
        return jsonify({
            'action': 'search',
            'products': products[:15],
            'message': voice_response.get('message', search_summary),
            'accessibility_summary': search_summary,
            'total_found': len(products),
            'showing_count': min(15, len(products)),
            'voice_optimized': True
        })
        
    except Exception as e:
        logging.error(f"Enhanced search error: {e}")
        return jsonify({
            'action': 'error',
            'message': 'Sorry, I couldn\'t search for products right now. Please try again.'
        })

def handle_voice_navigation(voice_response, user_session):
    """Handle voice navigation commands"""
    try:
        products_to_read = voice_response.get('products_to_read', [])
        navigation_context = voice_response.get('navigation_context', {})
        
        # Generate detailed voice descriptions for current page products
        if products_to_read:
            detailed_descriptions = []
            for i, product in enumerate(products_to_read, 1):
                page_offset = navigation_context.get('current_page', 1) - 1
                global_item_number = (page_offset * 5) + i  # Assuming 5 items per page
                
                description = accessibility_describer.describe_product_for_accessibility(
                    product, position=global_item_number
                )
                detailed_descriptions.append(description)
            
            full_message = voice_response.get('message', '') + " " + " ".join(detailed_descriptions)
        else:
            full_message = voice_response.get('message', '')
        
        return jsonify({
            'action': 'navigation',
            'message': full_message,
            'products': products_to_read,
            'navigation_context': navigation_context,
            'voice_optimized': True
        })
        
    except Exception as e:
        logging.error(f"Voice navigation error: {e}")
        return jsonify({
            'action': 'error',
            'message': 'Sorry, I couldn\'t process that navigation command.'
        })

def handle_voice_add_to_cart(voice_response, user_session):
    """Handle voice add to cart commands"""
    try:
        product = voice_response.get('product')
        if product:
            cart = user_session['cart']
            success, cart_message = cart.add_item(product)
            
            # Combine voice manager message with cart confirmation
            full_message = voice_response.get('message', '') + " " + cart_message
            
            return jsonify({
                'action': 'add_to_cart',
                'success': success,
                'message': full_message,
                'product': product,
                'cart_count': voice_response.get('cart_count', len(cart.cart.get('items', []))),
                'voice_optimized': True,
                'suggestions': voice_response.get('suggestions', [])
            })
        else:
            return jsonify(voice_response)
            
    except Exception as e:
        logging.error(f"Voice add to cart error: {e}")
        return jsonify({
            'action': 'error',
            'message': 'Sorry, I couldn\'t add that item to your cart.'
        })

def handle_voice_view_cart(voice_response, user_session):
    """Handle voice view cart commands"""
    try:
        cart = user_session['cart']
        cart_summary = cart.get_cart_summary()
        cart_items = cart.cart.get('items', [])
        total_amount = cart.get_total_amount()
        
        # Combine voice manager message with actual cart data
        return jsonify({
            'action': 'show_cart',
            'message': voice_response.get('message', cart_summary),
            'items': cart_items,
            'total': total_amount,
            'item_count': len(cart_items),
            'voice_optimized': True,
            'suggestions': voice_response.get('suggestions', [])
        })
        
    except Exception as e:
        logging.error(f"Voice view cart error: {e}")
        return jsonify({
            'action': 'error',
            'message': 'Sorry, I couldn\'t retrieve your cart.'
        })
    try:
        user_session = get_user_cart()
        keywords, min_price, max_price = parse_query(query)
        
        logging.info(f"Searching for: '{keywords}' with price range: {min_price}-{max_price}")
        
        products = []
        scraping_successful = False
        
        try:
            # Use multi-store scraper for comprehensive search
            products = multi_store_scraper.search_all_stores(keywords, min_price, max_price)
            
            if products and len(products) > 0:
                scraping_successful = True
                logging.info(f"Multi-store scraping successful: found {len(products)} products")
            else:
                logging.info("Multi-store search returned no results, trying Flipkart only")
                
        except Exception as scraping_error:
            logging.error(f"Multi-store scraping failed: {scraping_error}")
        
        # Fallback to single store if multi-store fails
        if not scraping_successful:
            try:
                products = search_flipkart(keywords, min_price, max_price)
                if products and len(products) > 0:
                    scraping_successful = True
                    logging.info(f"Flipkart fallback successful: found {len(products)} products")
                    
            except Exception as flipkart_error:
                logging.error(f"Flipkart scraping also failed: {flipkart_error}")
        
        # Enhanced fallback system if all scraping fails
        if not scraping_successful or not products:
            logging.info("Using enhanced fallback product system")
            products = enhanced_db.search_products(keywords, min_price, max_price)
            
            # Mark as fallback for transparency
            for product in products:
                product['fallback'] = True
        
        # Filter products by price if specified (redundant filtering for safety)
        if min_price or max_price:
            filtered_products = []
            for product in products:
                price = product.get('price', 0)
                if isinstance(price, str):
                    price = int(''.join(filter(str.isdigit, price)) or 0)
                
                if min_price and price < min_price:
                    continue
                if max_price and price > max_price:
                    continue
                filtered_products.append(product)
            products = filtered_products
        
        # Store products in user session
        user_session['current_products'] = products[:15]  # Show more products from multiple stores
        
        # Generate accessibility-friendly summary
        search_summary = accessibility_describer.create_search_summary_for_accessibility(
            products[:15], keywords
        )
        
        # Add fallback notice if using fallback products
        if products and products[0].get('fallback'):
            search_summary += " Note: Some results are from our curated product database due to temporary scraping limitations."
        
        return jsonify({
            'action': 'search',
            'products': products[:15],
            'message': search_summary,
            'accessibility_summary': search_summary,
            'total_found': len(products),
            'showing_count': min(15, len(products)),
            'using_fallback': products and products[0].get('fallback', False)
        })
        
    except Exception as e:
        logging.error(f"Search error: {e}")
        return jsonify({
            'action': 'error',
            'message': 'Sorry, I couldn\'t search for products right now. Please try again.'
        })

def handle_add_to_cart_api(command_data):
    try:
        user_session = get_user_cart()
        cart = user_session['cart']
        current_products = user_session['current_products']
        
        # Extract item number from command data
        item_number = command_data.get('item_number', 1) - 1
        
        if 0 <= item_number < len(current_products):
            product = current_products[item_number]
            success, message = cart.add_item(product)
            
            return jsonify({
                'action': 'add_to_cart',
                'success': success,
                'message': message,
                'product': product
            })
        else:
            return jsonify({
                'action': 'error',
                'message': 'Please specify a valid item number from the search results.'
            })
            
    except Exception as e:
        logging.error(f"Add to cart error: {e}")
        return jsonify({
            'action': 'error',
            'message': 'Sorry, I couldn\'t add that item to your cart.'
        })

def handle_view_cart_api():
    try:
        user_session = get_user_cart()
        cart = user_session['cart']
        
        cart_summary = cart.get_cart_summary()
        cart_items = cart.cart.get('items', [])
        total_amount = cart.get_total_amount()
        
        return jsonify({
            'action': 'show_cart',
            'message': cart_summary,
            'items': cart_items,
            'total': total_amount,
            'item_count': len(cart_items)
        })
        
    except Exception as e:
        logging.error(f"View cart error: {e}")
        return jsonify({
            'action': 'error',
            'message': 'Sorry, I couldn\'t retrieve your cart.'
        })

@app.route('/api/product-details', methods=['POST'])
def product_details_api():
    try:
        data = request.json
        item_number = data.get('item_number', 1) - 1
        
        user_session = get_user_cart()
        current_products = user_session['current_products']
        
        if 0 <= item_number < len(current_products):
            product = current_products[item_number]
            
            # Use accessibility-friendly description
            description = accessibility_describer.describe_product_for_accessibility(
                product, position=item_number + 1
            )
            
            return jsonify({
                'action': 'product_details',
                'message': description,
                'product': product,
                'accessibility_description': description
            })
        else:
            return jsonify({
                'action': 'error',
                'message': 'Please specify a valid item number from the current search results.'
            })
            
    except Exception as e:
        logging.error(f"Product details error: {e}")
        return jsonify({
            'action': 'error',
            'message': 'Sorry, I couldn\'t get the product details.'
        })

@app.route('/api/compare-products', methods=['POST'])
def compare_products_api():
    try:
        user_session = get_user_cart()
        current_products = user_session['current_products']
        
        if len(current_products) < 2:
            return jsonify({
                'action': 'error',
                'message': 'I need at least 2 products to compare. Please search for products first.'
            })
        
        # Compare top 5 products for better accessibility
        products_to_compare = current_products[:5]
        
        # Use accessibility-friendly comparison
        comparison = accessibility_describer.create_comparison_for_accessibility(products_to_compare)
        
        return jsonify({
            'action': 'compare',
            'message': comparison,
            'products': products_to_compare,
            'accessibility_comparison': comparison
        })
        
    except Exception as e:
        logging.error(f"Comparison error: {e}")
        return jsonify({
            'action': 'error',
            'message': 'Sorry, I couldn\'t compare the products.'
        })

@app.route('/api/checkout', methods=['POST'])
def checkout_api():
    try:
        user_session = get_user_cart()
        cart = user_session['cart']
        
        success, message = cart.proceed_to_checkout()
        
        return jsonify({
            'action': 'checkout',
            'success': success,
            'message': message
        })
        
    except Exception as e:
        logging.error(f"Checkout error: {e}")
        return jsonify({
            'action': 'error',
            'message': 'Sorry, there was an error processing your checkout.'
        })

@app.route('/api/help', methods=['GET'])
def help_api():
    help_text = """Available commands:
    - Search for products: 'Find shoes under 2000'
    - Add to cart: 'Add item 1 to cart'
    - View cart: 'Show my cart'
    - Checkout: 'Checkout'"""
    return jsonify({'help': help_text})

if __name__ == '__main__':
    app.run(debug=True, port=5002)  # Change to port 5002
