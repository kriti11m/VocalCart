from flask import Flask, request, jsonify
from flipkart_scraper import search_flipkart  # Make sure this function is defined in your flipkart_scraper.py
import logging

app = Flask(__name__)

# ✅ Root URL returns a welcome message
@app.route('/')
def home():
    return """
    <h1>🛍️ Welcome to VocalCart Server</h1>
    <p>Use the <code>/search?query=your+product&min_price=100&max_price=500</code> endpoint to fetch products.</p>
    """

# ✅ Product search endpoint
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    if not query:
        return jsonify({"error": "Missing required parameter 'query'"}), 400

    try:
        min_price = int(min_price) if min_price else None
        max_price = int(max_price) if max_price else None
    except ValueError:
        return jsonify({"error": "min_price and max_price should be integers"}), 400

    try:
        results = search_flipkart(query, min_price, max_price)
        return jsonify({"products": results})
    except Exception as e:
        logging.exception("Error during Flipkart scraping")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
