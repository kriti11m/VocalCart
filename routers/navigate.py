from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

class NavigationCommand(BaseModel):
    command: str  # "next", "previous", "repeat", "buy", "first", "last"
    session_id: Optional[str] = "default"
    item_number: Optional[int] = None

@router.post("/navigate")
async def handle_navigation(nav_cmd: NavigationCommand):
    """
    Handle navigation commands for browsing products
    Commands: next, previous, repeat, first, last, buy, item X
    All state is maintained in-memory (no database)
    """
    try:
        # Get session store from main app
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from fastapi_server import get_session_store
        session_store = get_session_store()
        
        session_id = nav_cmd.session_id
        command = nav_cmd.command.lower().strip()
        
        # Initialize session if not exists
        if session_id not in session_store:
            return {
                "success": False,
                "message": "No active session found. Please search for products first.",
                "voice_response": "Please search for products first before navigating."
            }
        
        session = session_store[session_id]
        products = session.get("current_products", [])
        current_index = session.get("current_index", 0)
        
        if not products:
            return {
                "success": False,
                "message": "No products available. Search for products first.",
                "voice_response": "No products found. Please search for products first."
            }
        
        logger.info(f"Navigation command: {command}, current_index: {current_index}, total_products: {len(products)}")
        
        # Handle different navigation commands
        if "next" in command:
            result = await _handle_next(session, products, current_index)
        elif "prev" in command or "previous" in command or "back" in command:
            result = await _handle_previous(session, products, current_index)
        elif "repeat" in command or "again" in command:
            result = await _handle_repeat(session, products, current_index)
        elif "first" in command:
            result = await _handle_first(session, products)
        elif "last" in command:
            result = await _handle_last(session, products)
        elif "buy" in command or "purchase" in command or "order" in command:
            result = await _handle_buy(session, products, current_index)
        elif "item" in command or nav_cmd.item_number:
            # Handle specific item selection
            item_num = nav_cmd.item_number or _extract_item_number(command)
            result = await _handle_item_selection(session, products, item_num)
        else:
            result = {
                "success": False,
                "message": f"Unknown navigation command: {command}",
                "voice_response": "I didn't understand that command. Try saying next, previous, repeat, or buy this."
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Navigation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "voice_response": "Sorry, I encountered an error with navigation."
        }

async def _handle_next(session: Dict, products: List[Dict], current_index: int) -> Dict:
    """Move to the next product"""
    if current_index < len(products) - 1:
        new_index = current_index + 1
        session["current_index"] = new_index
        product = products[new_index]
        
        voice_response = f"Next product: {product['title']} for rupees {product['price']}."
        if product.get('rating'):
            voice_response += f" Rating: {product['rating']} stars."
        voice_response += " Say buy this to purchase, or next for more options."
        
        return {
            "success": True,
            "action": "next",
            "current_index": new_index,
            "total_products": len(products),
            "product": product,
            "voice_response": voice_response
        }
    else:
        return {
            "success": False,
            "message": "You're already at the last product",
            "current_index": current_index,
            "total_products": len(products),
            "voice_response": "This is the last product. Say first to go back to the beginning, or search for new products."
        }

async def _handle_previous(session: Dict, products: List[Dict], current_index: int) -> Dict:
    """Move to the previous product"""
    if current_index > 0:
        new_index = current_index - 1
        session["current_index"] = new_index
        product = products[new_index]
        
        voice_response = f"Previous product: {product['title']} for rupees {product['price']}."
        if product.get('rating'):
            voice_response += f" Rating: {product['rating']} stars."
        voice_response += " Say buy this to purchase, or next for more options."
        
        return {
            "success": True,
            "action": "previous",
            "current_index": new_index,
            "total_products": len(products),
            "product": product,
            "voice_response": voice_response
        }
    else:
        return {
            "success": False,
            "message": "You're already at the first product",
            "current_index": current_index,
            "total_products": len(products),
            "voice_response": "This is the first product. Say next to move forward, or last to go to the end."
        }

async def _handle_repeat(session: Dict, products: List[Dict], current_index: int) -> Dict:
    """Repeat the current product information"""
    if current_index < len(products):
        product = products[current_index]
        
        voice_response = f"Current product: {product['title']} for rupees {product['price']}."
        if product.get('rating'):
            voice_response += f" Rating: {product['rating']} stars."
        if product.get('store'):
            voice_response += f" Available on {product['store']}."
        voice_response += " Say buy this to purchase, next for the next product, or previous to go back."
        
        return {
            "success": True,
            "action": "repeat",
            "current_index": current_index,
            "total_products": len(products),
            "product": product,
            "voice_response": voice_response
        }
    else:
        return {
            "success": False,
            "message": "No product to repeat",
            "voice_response": "No product available to repeat. Please search for products first."
        }

async def _handle_first(session: Dict, products: List[Dict]) -> Dict:
    """Go to the first product"""
    if products:
        session["current_index"] = 0
        product = products[0]
        
        voice_response = f"First product: {product['title']} for rupees {product['price']}."
        if product.get('rating'):
            voice_response += f" Rating: {product['rating']} stars."
        voice_response += " Say buy this to purchase, or next for more options."
        
        return {
            "success": True,
            "action": "first",
            "current_index": 0,
            "total_products": len(products),
            "product": product,
            "voice_response": voice_response
        }
    else:
        return {
            "success": False,
            "message": "No products available",
            "voice_response": "No products available. Please search for products first."
        }

async def _handle_last(session: Dict, products: List[Dict]) -> Dict:
    """Go to the last product"""
    if products:
        last_index = len(products) - 1
        session["current_index"] = last_index
        product = products[last_index]
        
        voice_response = f"Last product: {product['title']} for rupees {product['price']}."
        if product.get('rating'):
            voice_response += f" Rating: {product['rating']} stars."
        voice_response += " Say buy this to purchase, or previous to go back."
        
        return {
            "success": True,
            "action": "last",
            "current_index": last_index,
            "total_products": len(products),
            "product": product,
            "voice_response": voice_response
        }
    else:
        return {
            "success": False,
            "message": "No products available",
            "voice_response": "No products available. Please search for products first."
        }

async def _handle_buy(session: Dict, products: List[Dict], current_index: int) -> Dict:
    """Handle purchase intent for current product"""
    if current_index < len(products):
        product = products[current_index]
        
        # In a real application, this would integrate with e-commerce APIs
        # For now, we'll provide the product URL and purchase information
        
        voice_response = f"Great choice! You selected {product['title']} for rupees {product['price']}. "
        
        if product.get('url'):
            voice_response += f"I'm opening the product page for you to complete the purchase on {product.get('store', 'the store')}."
        else:
            voice_response += "This is a demo version. In the full app, you would be redirected to complete the purchase."
        
        return {
            "success": True,
            "action": "buy",
            "product": product,
            "current_index": current_index,
            "purchase_url": product.get('url', ''),
            "voice_response": voice_response,
            "next_steps": "Product page will open in browser" if product.get('url') else "Demo mode - no actual purchase"
        }
    else:
        return {
            "success": False,
            "message": "No product selected to buy",
            "voice_response": "No product selected. Please choose a product first, then say buy this."
        }

async def _handle_item_selection(session: Dict, products: List[Dict], item_number: Optional[int]) -> Dict:
    """Handle selection of a specific item by number"""
    if item_number is None:
        return {
            "success": False,
            "message": "No item number specified",
            "voice_response": "Please specify an item number, like 'show item 3' or 'go to product 2'."
        }
    
    # Convert to 0-based index
    index = item_number - 1
    
    if 0 <= index < len(products):
        session["current_index"] = index
        product = products[index]
        
        voice_response = f"Product {item_number}: {product['title']} for rupees {product['price']}."
        if product.get('rating'):
            voice_response += f" Rating: {product['rating']} stars."
        voice_response += " Say buy this to purchase, or next for more options."
        
        return {
            "success": True,
            "action": "select_item",
            "current_index": index,
            "item_number": item_number,
            "total_products": len(products),
            "product": product,
            "voice_response": voice_response
        }
    else:
        return {
            "success": False,
            "message": f"Item {item_number} not found",
            "total_products": len(products),
            "voice_response": f"Item {item_number} is not available. I have {len(products)} products. Please choose a number between 1 and {len(products)}."
        }

def _extract_item_number(command: str) -> Optional[int]:
    """Extract item number from command text"""
    import re
    
    patterns = [
        r'item\s+(\d+)',
        r'number\s+(\d+)', 
        r'product\s+(\d+)',
        r'option\s+(\d+)',
        r'(\d+)(?:st|nd|rd|th)?\s+(?:item|product|option)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, command.lower())
        if match:
            try:
                return int(match.group(1))
            except (IndexError, ValueError):
                continue
    
    return None

@router.get("/navigate/session/{session_id}")
async def get_navigation_state(session_id: str):
    """Get current navigation state for a session"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from fastapi_server import get_session_store
        session_store = get_session_store()
        
        if session_id not in session_store:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = session_store[session_id]
        products = session.get("current_products", [])
        current_index = session.get("current_index", 0)
        
        current_product = products[current_index] if current_index < len(products) else None
        
        return {
            "session_id": session_id,
            "total_products": len(products),
            "current_index": current_index,
            "current_product": current_product,
            "has_next": current_index < len(products) - 1,
            "has_previous": current_index > 0,
            "last_query": session.get("last_query", "")
        }
        
    except Exception as e:
        logger.error(f"Error getting navigation state: {e}")
        raise HTTPException(status_code=500, detail=str(e))
