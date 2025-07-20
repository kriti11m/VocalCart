from voice_input import get_voice_input
from voice_output import speak
from query_parser import parse_query
from flipkart_scraper import search_flipkart  # next we'll write this

while True:
    speak("Please tell me what you're looking for.")
    query = get_voice_input()

    if query:
        keywords, min_price, max_price = parse_query(query)
        print("Parsed Query:", keywords, min_price, max_price)
        products = search_flipkart(keywords, min_price, max_price)
        
        # Just print for now
        for i, product in enumerate(products[:5]):
            speak(f"Option {i+1}: {product['title']} for Rs {product['price']}")
