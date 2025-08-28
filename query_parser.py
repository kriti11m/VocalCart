import re

def parse_query(text):
    if not text or text.strip() == "":
        return "shoes", None, None
    
    # Don't process error messages
    if "sorry" in text.lower() or "didn't catch" in text.lower():
        return "shoes", None, 2000
    
    text = text.lower().strip()
    
    # Remove common command words that might interfere
    text = re.sub(r'\b(search for|find|look for|show me|get me)\b', '', text).strip()
    
    min_price, max_price = None, None

    # Between or from ... to ...
    match = re.search(r'(?:between|from)\s+(\d+)\s+(?:and|to)\s+(\d+)', text)
    if match:
        min_price = int(match.group(1))
        max_price = int(match.group(2))
    # Under, less than, below, upto
    elif match := re.search(r'(under|less than|below|upto)\s+(\d+)', text):
        max_price = int(match.group(2))
    # More than, above
    elif match := re.search(r'(more than|above)\s+(\d+)', text):
        min_price = int(match.group(2))
    # Only one number mentioned (assume it's max price)
    elif match := re.search(r'(\d+)', text):
        max_price = int(match.group(1))

    # Extract keywords by removing price-related words and numbers
    keywords = re.sub(r'\b(under|below|less than|more than|above|between|upto|from|to|rs|rupees|price|cost)\b', '', text)
    keywords = re.sub(r'\d+', '', keywords)
    keywords = re.sub(r'\s+', ' ', keywords).strip()
    
    # If no keywords found, default to "shoes"
    if not keywords or len(keywords) < 2:
        keywords = "shoes"

    return keywords, min_price, max_price
