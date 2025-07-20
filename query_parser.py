import re

def parse_query(text):
    if not text:
        return "sorry, i didn't catch that.", None, None

    text = text.lower()
    keywords = re.sub(r'\b(under|below|less than|more than|above|between|upto|from|to|rs|rupees)\b', '', text)
    keywords = re.sub(r'\d+', '', keywords).strip()

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

    # Re-extract keywords without price parts
    keywords = re.sub(r'(between|from|under|less than|below|more than|above|upto|to|and)?\s*\d+(\s*to\s*\d+)?', '', text).strip()

    return keywords.strip(), min_price, max_price
