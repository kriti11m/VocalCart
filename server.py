from flask import Flask, render_template, request, jsonify
import json
from voice_input import get_voice_input
from voice_output import speak
from query_parser import parse_query
from command_parser import parse_command
from flipkart_scraper import search_flipkart
from shopping_cart import ShoppingCart
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
logging.basicConfig(level=logging.INFO)

# Global cart (in production, use sessions or database)
user_carts = {}

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/api/voice-input', methods=['POST'])
def voice_input_api():
    try:
        audio_data = request.json.get('audio_data')
        # Process voice input
        result = voice_input.listen_for_command()
        return jsonify({'success': True, 'command': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/voice-output', methods=['POST'])
def voice_output_api():
    text = request.json.get('text')
    voice_output.speak(text)
    return jsonify({'success': True})

@app.route('/api/compare-products', methods=['GET'])
def compare_products_api():
    products = session.get('current_products', [])
    comparison = product_description.compare_products(products)
    return jsonify({'comparison': comparison})

@app.route('/api/help', methods=['GET'])
def help_api():
    help_text = """Available commands:
    - Search for products: 'Find shoes under 2000'
    - Add to cart: 'Add item 1 to cart'
    - View cart: 'Show my cart'
    - Checkout: 'Checkout'"""
    return jsonify({'help': help_text})

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change from port 5000 to 5001
