from flask import Flask, render_template, request, jsonify
from voice_input import get_voice_input
from voice_output import speak
from query_parser import parse_query
from command_parser import parse_command
from flipkart_scraper import search_flipkart
from shopping_cart import ShoppingCart
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Global cart (in production, use sessions or database)
user_carts = {}

@app.route('/')
def index():
    return render_template('voice_shop.html')

@app.route('/api/voice-command', methods=['POST'])
def handle_voice_command():
    try:
        data = request.json
        command = data.get('command', '').lower()
        
        # Parse the command
        command_type, command_data = parse_command(command)
        
        if command_type == "search":
            return handle_search_api(command)
        elif command_type == "add_to_cart":
            return handle_add_to_cart_api(command_data)
        elif command_type == "view_cart":
            return handle_view_cart_api()
        else:
            return jsonify({
                'action': 'message',
                'message': 'I understand you want to: ' + command
            })
            
    except Exception as e:
        logging.error(f"API Error: {e}")
        return jsonify({
            'action': 'error',
            'message': 'Sorry, I encountered an error processing your request.'
        }), 500

def handle_search_api(query):
    try:
        keywords, min_price, max_price = parse_query(query)
        products = search_flipkart(keywords, min_price, max_price)
        
        return jsonify({
            'action': 'search',
            'products': products[:10],
            'message': f'Found {len(products)} products matching your search.'
        })
    except Exception as e:
        logging.error(f"Search error: {e}")
        return jsonify({
            'action': 'error',
            'message': 'Sorry, I couldn\'t search for products right now.'
        })

def handle_add_to_cart_api(command_data):
    # Implementation for adding to cart via API
    return jsonify({
        'action': 'add_to_cart',
        'message': 'Item added to cart!'
    })

def handle_view_cart_api():
    # Implementation for viewing cart via API
    return jsonify({
        'action': 'show_cart',
        'message': 'Your cart is empty.'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
