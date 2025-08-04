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
        r'purchase (\d+)'
    ]
    
    for pattern in add_patterns:
        match = re.search(pattern, query)
        if match:
            return "add_to_cart", {"item_number": int(match.group(1))}
    
    # Cart operations
    if any(phrase in query for phrase in ['show cart', 'view cart', 'my cart', 'cart']):
        return "view_cart", {}
    
    # Product details
    detail_patterns = [
        r'tell me about item (\d+)',
        r'details of item (\d+)',
        r'more about (\d+)'
    ]
    
    for pattern in detail_patterns:
        match = re.search(pattern, query)
        if match:
            return "product_details", {"item_number": int(match.group(1))}
    
    # Checkout
    if any(word in query for word in ['checkout', 'buy now', 'purchase', 'order']):
        return "checkout", {}
    
    # Help
    if any(word in query for word in ['help', 'commands', 'what can you do']):
        return "help", {}
    
    # Exit
    if any(word in query for word in ['exit', 'quit', 'bye', 'goodbye']):
        return "exit", {}
    
    return "unknown", {"query": query}
