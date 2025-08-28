import re

def parse_command(query):
    """Parse voice commands and extract intent and data"""
    query = query.lower().strip()
    
    # Search patterns
    if any(word in query for word in ['search', 'find', 'look for', 'show me']):
        return "search", {"query": query}
    
    # Add to cart patterns
    add_patterns = [
        r'add item (\d+)',
        r'add (\d+)',
        r'buy item (\d+)',
        r'purchase item (\d+)',
        r'add product (\d+)'
    ]
    
    for pattern in add_patterns:
        match = re.search(pattern, query)
        if match:
            return "add_to_cart", {"item_number": int(match.group(1))}
    
    # Remove from cart patterns
    remove_patterns = [
        r'remove item (\d+)',
        r'delete item (\d+)',
        r'remove (\d+) from cart',
        r'take out item (\d+)'
    ]
    
    for pattern in remove_patterns:
        match = re.search(pattern, query)
        if match:
            return "remove_from_cart", {"item_number": int(match.group(1))}
    
    # Cart operations
    if any(phrase in query for phrase in ['show cart', 'view cart', 'my cart', 'cart', 'shopping cart']):
        return "view_cart", {}
    
    # Clear cart
    if any(phrase in query for phrase in ['clear cart', 'empty cart', 'remove all items']):
        return "clear_cart", {}
    
    # Product details
    detail_patterns = [
        r'tell me about item (\d+)',
        r'details of item (\d+)',
        r'more about (\d+)',
        r'details for product (\d+)',
        r'info on item (\d+)'
    ]
    
    for pattern in detail_patterns:
        match = re.search(pattern, query)
        if match:
            return "product_details", {"item_number": int(match.group(1))}
    
    # Compare products
    if any(phrase in query for phrase in ['compare products', 'compare items', 'show comparison']):
        return "compare", {}
    
    # Checkout
    if any(word in query for word in ['checkout', 'buy now', 'complete order', 'finish order', 'place order']):
        return "checkout", {}
    
    # Help
    if any(word in query for word in ['help', 'commands', 'what can you do', 'how does this work']):
        return "help", {}
    
    # Exit
    if any(word in query for word in ['exit', 'quit', 'bye', 'goodbye', 'close']):
        return "exit", {}
    
    return "unknown", {"query": query}
