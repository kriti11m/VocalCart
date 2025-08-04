import re
import random

def generate_detailed_description(product, index=None):
    """Generate a detailed, voice-friendly product description"""
    title = product.get('title', 'Unknown product')
    price = product.get('price', 'Price not available')
    rating = product.get('rating', 'No rating')
    
    # Clean and enhance title for voice
    clean_title = clean_title_for_voice(title)
    
    # Format price for voice
    price_text = format_price_for_voice(price)
    
    # Create detailed description
    description_parts = []
    
    if index:
        description_parts.append(f"Option {index}:")
    
    description_parts.append(clean_title)
    description_parts.append(f"Priced at {price_text}")
    
    if rating and rating != 'No rating':
        description_parts.append(f"Customer rating: {rating} stars")
    
    # Add category hints based on title keywords
    category_info = get_category_info(title)
    if category_info:
        description_parts.append(category_info)
    
    return ". ".join(description_parts) + "."

def clean_title_for_voice(title):
    """Clean product title to be more voice-friendly"""
    # Remove excessive punctuation and symbols
    title = re.sub(r'[^\w\s\-\(\)]', ' ', title)
    
    # Replace common abbreviations with full words
    replacements = {
        'mens': "men's",
        'womens': "women's",
        'kids': "children's",
        'xl': 'extra large',
        'lg': 'large',
        'sm': 'small',
        'xs': 'extra small',
        'ml': 'milliliters',
        'kg': 'kilograms',
        'gm': 'grams',
        'cm': 'centimeters',
        'mm': 'millimeters',
        'led': 'L E D',
        'usb': 'U S B',
        'wifi': 'Wi-Fi',
        'bluetooth': 'Bluetooth'
    }
    
    for abbr, full in replacements.items():
        title = re.sub(r'\b' + abbr + r'\b', full, title, flags=re.IGNORECASE)
    
    # Clean up extra spaces
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title

def format_price_for_voice(price):
    """Format price to be voice-friendly"""
    if isinstance(price, (int, float)):
        if price >= 1000:
            thousands = price // 1000
            remainder = price % 1000
            if remainder == 0:
                return f"{thousands} thousand rupees"
            else:
                return f"{thousands} thousand {remainder} rupees"
        else:
            return f"{price} rupees"
    elif isinstance(price, str):
        # Extract number from string
        price_match = re.search(r'[\d,]+', str(price))
        if price_match:
            price_num = int(price_match.group().replace(',', ''))
            return format_price_for_voice(price_num)
    
    return str(price)

def get_category_info(title):
    """Provide category-specific information based on title keywords"""
    title_lower = title.lower()
    
    if any(word in title_lower for word in ['shoe', 'sneaker', 'boot', 'sandal', 'slipper']):
        return "This is a footwear item"
    elif any(word in title_lower for word in ['shirt', 'tshirt', 't-shirt', 'top', 'blouse']):
        return "This is a clothing item for the upper body"
    elif any(word in title_lower for word in ['pant', 'jean', 'trouser', 'short']):
        return "This is a clothing item for the lower body"
    elif any(word in title_lower for word in ['phone', 'mobile', 'smartphone']):
        return "This is a mobile device"
    elif any(word in title_lower for word in ['laptop', 'computer', 'pc']):
        return "This is a computing device"
    elif any(word in title_lower for word in ['book', 'novel', 'guide']):
        return "This is a book or reading material"
    elif any(word in title_lower for word in ['watch', 'clock', 'timer']):
        return "This is a timepiece"
    elif any(word in title_lower for word in ['bag', 'backpack', 'purse', 'wallet']):
        return "This is a bag or accessory"
    
    return None

def create_comparison_description(products):
    """Create a voice-friendly comparison of multiple products"""
    if len(products) < 2:
        return "I need at least 2 products to compare."
    
    comparison_parts = [f"Comparing {len(products)} products:"]
    
    for i, product in enumerate(products, 1):
        title = clean_title_for_voice(product.get('title', 'Unknown'))
        price = format_price_for_voice(product.get('price', 0))
        comparison_parts.append(f"Option {i}: {title} at {price}")
    
    # Find cheapest and most expensive
    prices = []
    for product in products:
        price = product.get('price', 0)
        if isinstance(price, str):
            price_match = re.search(r'[\d,]+', price)
            if price_match:
                price = int(price_match.group().replace(',', ''))
        prices.append(price)
    
    if prices:
        min_price_idx = prices.index(min(prices))
        max_price_idx = prices.index(max(prices))
        
        comparison_parts.append(f"The most affordable option is option {min_price_idx + 1}")
        if min_price_idx != max_price_idx:
            comparison_parts.append(f"The most expensive option is option {max_price_idx + 1}")
    
    return ". ".join(comparison_parts) + "."

def get_help_text():
    """Provide help information about available commands"""
    help_text = """
    Here are the commands you can use:
    
    To search: Say 'find' or 'search' followed by what you want, like 'find white shoes under 500 rupees'.
    
    To navigate: Say 'next' for the next product, 'previous' for the last one, or 'repeat' to hear the current product again.
    
    To get details: Say 'details' or 'tell me more' about the current product.
    
    To compare: Say 'compare' to compare the current products.
    
    To select: Say 'select' or 'choose' followed by a number, like 'select 2'.
    
    To purchase: Say 'buy' or 'purchase' to proceed with buying the current product.
    
    To manage cart: Say 'add to cart', 'show cart', or 'remove from cart'.
    
    To ask specific questions: Ask about 'price', 'rating', 'description', or 'availability'.
    
    To exit: Say 'exit', 'quit', or 'bye' to stop the application.
    
    To start over: Say 'restart' or 'new search' to begin a fresh search.
    """
    return help_text.strip()

def describe_product(product):
    """Generate a voice-friendly description of a product"""
    try:
        title = product.get('title', 'Unknown Product')
        price = product.get('price', 'Price not available')
        
        # Clean up the title for better voice output
        clean_title = title.replace('|', ',').replace('&', 'and')
        
        description = f"This is {clean_title}. It's priced at rupees {price}."
        
        # Add additional details if available
        if 'rating' in product:
            description += f" It has a rating of {product['rating']} stars."
            
        if 'reviews' in product:
            description += f" Based on {product['reviews']} customer reviews."
            
        return description
        
    except Exception as e:
        return "Sorry, I couldn't get the details for this product."

def compare_products(products):
    """Compare multiple products and provide voice-friendly comparison"""
    try:
        if len(products) < 2:
            return "I need at least 2 products to compare."
            
        comparison = "Here's a comparison of the products: "
        
        for i, product in enumerate(products[:3], 1):  # Compare max 3 products
            title = product.get('title', f'Product {i}')[:50]  # Truncate long titles
            price = product.get('price', 'Unknown price')
            
            comparison += f"Product {i}: {title} costs rupees {price}. "
            
        # Find cheapest and most expensive
        prices = []
        for product in products:
            try:
                # Extract numeric price
                price_str = product.get('price', '0').replace(',', '').replace('₹', '').replace('Rs', '')
                price_num = float(''.join(filter(str.isdigit, price_str)))
                prices.append(price_num)
            except:
                prices.append(0)
                
        if prices:
            min_idx = prices.index(min(prices))
            max_idx = prices.index(max(prices))
            
            comparison += f"The most affordable option is product {min_idx + 1}. "
            comparison += f"The most expensive is product {max_idx + 1}."
            
        return comparison
        
    except Exception as e:
        return "Sorry, I couldn't compare these products."

def generate_product_summary(products):
    """Generate a summary of search results"""
    if not products:
        return "No products found."
        
    try:
        total_products = len(products)
        
        # Calculate price range
        prices = []
        for product in products:
            try:
                price_str = product.get('price', '0').replace(',', '').replace('₹', '').replace('Rs', '')
                price_num = float(''.join(filter(str.isdigit, price_str)))
                prices.append(price_num)
            except:
                continue
                
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) / len(prices)
            
            summary = f"I found {total_products} products. "
            summary += f"Prices range from {format_price_for_speech(str(min_price))} "
            summary += f"to {format_price_for_speech(str(max_price))}. "
            summary += f"The average price is {format_price_for_speech(str(int(avg_price)))}."
        else:
            summary = f"I found {total_products} products for you."
            
        return summary
        
    except Exception as e:
        return f"I found {len(products)} products for you."

def format_price_for_speech(price_str):
    """Convert price string to speech-friendly format"""
    try:
        # Remove currency symbols and commas
        clean_price = price_str.replace('₹', '').replace('Rs', '').replace(',', '').strip()
        
        # Convert to number and back for proper formatting
        price_num = float(clean_price)
        
        if price_num >= 100000:
            return f"{price_num/100000:.1f} lakh rupees"
        elif price_num >= 1000:
            return f"{price_num/1000:.1f} thousand rupees"
        else:
            return f"{int(price_num)} rupees"
            
    except:
        return price_str

def get_product_help():
    """Provide help about product features"""
    help_text = """
    I can help you with:
    - Getting detailed information about any product
    - Comparing up to 3 products at once
    - Finding the best deals in your search results
    - Reading customer ratings and reviews
    
    Just say things like:
    - Tell me about item 1
    - Compare items 1, 2 and 3
    - Which is the cheapest option?
    """
    return help_text
