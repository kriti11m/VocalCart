import asyncio
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import logging
import uvicorn
from typing import Optional, Dict, List
import json
import time
import threading
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="VocalCart API",
    description="Real-time voice-powered shopping assistant with live product scraping",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory session storage (no database)
# In production, use Redis or similar for multi-instance deployments
session_store: Dict[str, Dict] = {}

# Initialize services
query_parser = None
voice_manager = None
scraper_pool = ThreadPoolExecutor(max_workers=4)

# Pydantic models for API requests
class VoiceCommand(BaseModel):
    command: str
    session_id: Optional[str] = "default"

class NavigationCommand(BaseModel):
    command: str  # "next", "previous", "repeat", "buy"
    session_id: Optional[str] = "default"

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "en"
    speed: Optional[float] = 1.0

# Include routers with dynamic imports
@app.on_event("startup")
async def startup_event():
    """Initialize services and routers on startup"""
    global query_parser, voice_manager
    
    try:
        # Import and initialize services
        from services.parser import QueryParser
        from utils.voice import VoiceManager
        
        query_parser = QueryParser()
        voice_manager = VoiceManager()
        
        # Import and include routers
        from routers import search, navigate, tts
        app.include_router(search.router, prefix="/api", tags=["search"])
        app.include_router(navigate.router, prefix="/api", tags=["navigation"])
        app.include_router(tts.router, prefix="/api", tags=["voice"])
        
        logger.info("VocalCart API startup complete")
        
    except ImportError as e:
        logger.warning(f"Some features may not be available due to missing dependencies: {e}")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.get("/")
async def root():
    """Health check and API info"""
    return {
        "message": "VocalCart API - Real-time Voice Shopping",
        "version": "2.0.0",
        "features": [
            "Real-time product scraping",
            "Voice command processing",
            "Multi-store search",
            "No database dependency",
            "In-memory session management"
        ],
        "endpoints": {
            "search": "/api/search",
            "navigate": "/api/navigate", 
            "voice-command": "/api/voice-command",
            "tts": "/api/tts"
        }
    }

@app.post("/api/voice-command")
async def process_voice_command(voice_cmd: VoiceCommand, background_tasks: BackgroundTasks):
    """
    Main endpoint for processing voice commands
    Determines if it's a search or navigation command and routes accordingly
    """
    try:
        session_id = voice_cmd.session_id
        command = voice_cmd.command.lower().strip()
        
        logger.info(f"Processing voice command: {command} for session: {session_id}")
        
        # Initialize session if not exists
        if session_id not in session_store:
            session_store[session_id] = {
                "current_products": [],
                "current_index": 0,
                "last_query": "",
                "session_active": True
            }
        
        session = session_store[session_id]
        
        # Parse command type
        global query_parser
        if query_parser is None:
            try:
                from services.parser import QueryParser
                query_parser = QueryParser()
            except Exception as e:
                logger.warning(f"Could not import QueryParser: {e}")
                # Simple fallback parser
                class SimpleParser:
                    def parse_command_type(self, cmd):
                        if any(word in cmd.lower() for word in ['next', 'previous', 'repeat', 'buy']):
                            return {"type": "navigation"}
                        return {"type": "search"}
                query_parser = SimpleParser()
            
        parsed_command = query_parser.parse_command_type(command)
        
        if parsed_command["type"] == "search":
            # Handle search directly to avoid circular imports
            try:
                # Extract price info from command
                import re
                min_price = None
                max_price = None
                
                # More robust price extraction
                under_match = re.search(r'under\s+(\d+)', command)
                if under_match:
                    max_price = int(under_match.group(1))
                
                range_match = re.search(r'between\s+(\d+)\s+and\s+(\d+)', command)
                if range_match:
                    min_price = int(range_match.group(1))
                    max_price = int(range_match.group(2))
                
                # Start a background task for real-time scraping
                def search_bg_task():
                    try:
                        from services.scraper_flipkart import FlipkartScraper
                        scraper = FlipkartScraper()
                        products = scraper.search(command, min_price, max_price)
                        
                        # Update session with real-time data
                        if products:
                            session["current_products"] = products
                            session["current_index"] = 0
                            session["last_query"] = command
                            logger.info(f"Background task completed with {len(products)} real-time products")
                        else:
                            logger.warning("Background scraping found no products")
                    except Exception as e:
                        logger.error(f"Background search error: {e}")
                
                # Start the background task
                background_tasks.add_task(search_bg_task)
                
                # Return an immediate response
                return {
                    "success": True,
                    "message": "Search started. Real-time products will be loaded shortly.",
                    "voice_response": "Searching for products in real-time. Please wait a moment.",
                    "session_id": session_id,
                    "status": "processing"
                }
                
            except Exception as e:
                logger.error(f"Search error: {e}")
                return {
                    "success": False,
                    "error": f"Search failed: {str(e)}",
                    "voice_response": "Sorry, I'm having trouble searching right now."
                }
            
        elif parsed_command["type"] == "navigation":
            # Handle navigation directly
            try:
                current_products = session.get("current_products", [])
                current_index = session.get("current_index", 0)
                
                if not current_products:
                    return {
                        "success": False,
                        "message": "No products to navigate. Please search first.",
                        "voice_response": "No products available. Please search for products first."
                    }
                
                if "next" in command:
                    if current_index < len(current_products) - 1:
                        new_index = current_index + 1
                        session["current_index"] = new_index
                        product = current_products[new_index]
                        voice_response = f"Next product: {product['title']} for rupees {product['price']}. Say buy this to purchase or next for more options."
                        return {
                            "success": True,
                            "action": "next",
                            "product": product,
                            "current_index": new_index,
                            "voice_response": voice_response
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Already at last product",
                            "voice_response": "This is the last product. Say first to go back to the beginning."
                        }
                
                elif "previous" in command or "prev" in command:
                    if current_index > 0:
                        new_index = current_index - 1
                        session["current_index"] = new_index
                        product = current_products[new_index]
                        voice_response = f"Previous product: {product['title']} for rupees {product['price']}. Say buy this to purchase or next for more options."
                        return {
                            "success": True,
                            "action": "previous",
                            "product": product,
                            "current_index": new_index,
                            "voice_response": voice_response
                        }
                    else:
                        return {
                            "success": False,
                            "message": "Already at first product",
                            "voice_response": "This is the first product. Say next to move forward."
                        }
                
                elif "buy" in command:
                    if current_index < len(current_products):
                        product = current_products[current_index]
                        voice_response = f"Great choice! You selected {product['title']} for rupees {product['price']}. Opening the product page for you."
                        return {
                            "success": True,
                            "action": "buy",
                            "product": product,
                            "voice_response": voice_response
                        }
                
                elif "repeat" in command:
                    if current_index < len(current_products):
                        product = current_products[current_index]
                        voice_response = f"Current product: {product['title']} for rupees {product['price']}. Say buy this to purchase, next for more options, or previous to go back."
                        return {
                            "success": True,
                            "action": "repeat",
                            "product": product,
                            "voice_response": voice_response
                        }
                
                # Default case
                return {
                    "success": False,
                    "message": "Navigation command not recognized",
                    "voice_response": "I didn't understand that navigation command. Try saying next, previous, repeat, or buy this."
                }
                
            except Exception as e:
                logger.error(f"Navigation error: {e}")
                return {
                    "success": False,
                    "error": f"Navigation failed: {str(e)}",
                    "voice_response": "Sorry, I had trouble with that navigation command."
                }
            
        elif parsed_command["type"] == "info":
            # Handle info requests about current product
            if not session["current_products"]:
                return {
                    "success": False,
                    "message": "No products to show info for. Please search first.",
                    "voice_response": "No products available. Please search for products first."
                }
            
            current_idx = session["current_index"]
            if current_idx < len(session["current_products"]):
                product = session["current_products"][current_idx]
                response_text = f"Product details: {product['title']}. Price: rupees {product['price']}."
                if "description" in product:
                    response_text += f" Description: {product['description']}"
                
                return {
                    "success": True,
                    "product": product,
                    "voice_response": response_text
                }
            
        else:
            # Default to search for unknown commands
            return {
                "success": False,
                "message": "Command not recognized. Try searching for products or navigation commands.",
                "voice_response": "I didn't understand that command. Try searching for products like 'find shoes under 2000 rupees' or navigation commands like next, previous, or buy this."
            }
            
    except Exception as e:
        logger.error(f"Error processing voice command: {e}")
        return {
            "success": False,
            "error": str(e),
            "voice_response": "Sorry, I encountered an error processing your request."
        }

@app.get("/api/search-status/{session_id}")
async def get_search_status(session_id: str):
    """Get the status and results of a background search"""
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = session_store[session_id]
    products = session.get("current_products", [])
    
    if products:
        first_product = products[0]
        voice_response = f"Found {len(products)} real-time products. First result: {first_product['title']} for rupees {first_product['price']}. Say next for more options or buy this to purchase."
        return {
            "success": True,
            "status": "complete",
            "products": products,
            "total_found": len(products),
            "voice_response": voice_response,
            "session_id": session_id
        }
    else:
        return {
            "success": False,
            "status": "processing",
            "message": "Still searching for products. Please try again in a moment.",
            "session_id": session_id
        }

@app.get("/api/session/{session_id}")
async def get_session_info(session_id: str):
    """Get current session information"""
    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = session_store[session_id]
    return {
        "session_id": session_id,
        "products_count": len(session["current_products"]),
        "current_index": session["current_index"],
        "last_query": session["last_query"],
        "session_active": session["session_active"]
    }

@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear session data"""
    if session_id in session_store:
        del session_store[session_id]
        return {"message": f"Session {session_id} cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(session_store),
        "service": "VocalCart API v2.0"
    }

# Export session store for use in routers
def get_session_store():
    return session_store

if __name__ == "__main__":
    uvicorn.run(
        "fastapi_server_improved:app",
        host="0.0.0.0",
        port=5004,  # Use a different port to avoid conflicts
        reload=True,
        log_level="info"
    )
