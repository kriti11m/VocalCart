import re

def parse_command(text):
    text = text.lower()
    if "next" in text:
        return {"action": "next"}
    if "repeat" in text:
        return {"action": "repeat"}
    if "stop" in text or "exit" in text:
        return {"action": "stop"}

    # Pattern: "<color> <product> under <price>"
    pattern = re.search(r"(?P<color>\w+)?\s?(?P<item>\w+)?\s?(?:under|below)?\s?(?P<price>\d+)?", text)
    if pattern:
        return {
            "action": "search",
            "color": pattern.group("color"),
            "item": pattern.group("item"),
            "price": pattern.group("price"),
        }

    return {"action": "unknown"}
