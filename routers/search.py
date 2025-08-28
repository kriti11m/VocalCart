from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Thread pool for concurrent scraping
executor = ThreadPoolExecutor(max_workers=3)

# Initialize services (lazy loading to avoid circular imports)
flipkart_scraper = None
amazon_scraper = None
multi_scraper = None
query_parser = None

def get_scrapers():
    """Initialize scrapers lazily"""
    global flipkart_scraper, amazon_scraper, multi_scraper, query_parser
    
    if flipkart_scraper is None:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        
        from services.scraper_flipkart import FlipkartScraper
        from services.scraper_amazon import AmazonScraper
        from services.multi_store_scraper import MultiStoreScraper
        from services.parser import QueryParser
        
        flipkart_scraper = FlipkartScraper()
        amazon_scraper = AmazonScraper()
        multi_scraper = MultiStoreScraper()
        query_parser = QueryParser()
    
    return flipkart_scraper, amazon_scraper, multi_scraper, query_parser

# Thread pool for concurrent scraping
executor = ThreadPoolExecutor(max_workers=3)

class SearchRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"
    max_results: Optional[int] = 20
    stores: Optional[List[str]] = ["flipkart", "amazon"]
    min_price: Optional[int] = None
    max_price: Optional[int] = None

class VoiceCommand(BaseModel):
    command: str
    session_id: Optional[str] = "default"

@router.post("/search")
async def search_products(request: SearchRequest):
    """
    Search for products across multiple e-commerce stores in real-time
    Returns a status response immediately and runs search in background
    """
    try:
        # Parse the search query
        _, _, _, query_parser = get_scrapers()
        parsed_query = query_parser.parse_search_query(
            request.query, 
            request.min_price, 
            request.max_price
        )
        
        logger.info(f"Searching for: {parsed_query}")
        
        # Get session store from main app
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from fastapi_server import get_session_store
        session_store = get_session_store()
        
        # Initialize session if not exists
        if request.session_id not in session_store:
            session_store[request.session_id] = {
                "current_products": [],
                "current_index": 0,
                "last_query": "",
                "session_active": True
            }
        
        session = session_store[request.session_id]
        
        # Clear any existing products to indicate search is in progress
        session["current_products"] = []
        session["last_query"] = request.query
        
        # Start background task for real-time scraping
        asyncio.create_task(
            background_search(
                request,
                parsed_query,
                session
            )
        )
        
        # Return immediate response
        return {
            "status": "processing",
            "message": "Search in progress. Use /api/search-status/{session_id} to check status.",
            "session_id": request.session_id,
            "voice_response": "Searching for real-time products. This might take a moment."
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "voice_response": "Sorry, I encountered an error while searching. Please try again."
        }

async def background_search(request: SearchRequest, parsed_query: Dict, session: Dict):
    """Run the search process in a background task"""
    try:
        # Prepare concurrent scraping tasks
        flipkart_scraper, amazon_scraper, multi_scraper, _ = get_scrapers()
        tasks = []
        
        if "flipkart" in request.stores:
            tasks.append(asyncio.create_task(
                asyncio.get_event_loop().run_in_executor(
                    executor,
                    flipkart_scraper.search,
                    parsed_query["keywords"],
                    parsed_query["min_price"],
                    parsed_query["max_price"]
                )
            ))
        
        if "amazon" in request.stores:
            tasks.append(asyncio.create_task(
                asyncio.get_event_loop().run_in_executor(
                    executor,
                    amazon_scraper.search,
                    parsed_query["keywords"],
                    parsed_query["min_price"],
                    parsed_query["max_price"]
                )
            ))
        
        # Execute all scraping tasks concurrently with a timeout
        results = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=30.0  # Set a reasonable timeout for scraping
        )
        
        # Combine and process results
        all_products = []
        
        for result in results:
            if not isinstance(result, Exception) and result:
                # Mark all as real-time data
                for product in result:
                    product['data_source'] = 'real-time'
                all_products.extend(result)
        
        # Sort by relevance and price
        all_products = sorted(all_products, key=lambda x: x.get('price', float('inf')))
        
        # Limit results
        limited_products = all_products[:request.max_results]
        
        # Update session with new results
        session["current_products"] = limited_products
        session["current_index"] = 0
        
        logger.info(f"Background search completed: found {len(limited_products)} products")
        
    except asyncio.TimeoutError:
        logger.warning(f"Search timed out for query: {request.query}")
        # Even if we time out, save any results we did get
        session["current_products"] = all_products[:request.max_results] if 'all_products' in locals() else []
    except Exception as e:
        logger.error(f"Background search error: {e}")
        # Leave session["current_products"] empty to indicate error

@router.post("/voice-search")
async def search_products_from_voice(voice_cmd: VoiceCommand):
    """
    Handle voice command and convert to search request
    Called from main voice command endpoint
    """
    try:
        # Parse voice command to extract search parameters
        _, _, _, query_parser = get_scrapers()
        parsed = query_parser.parse_search_query(voice_cmd.command)
        
        # Create search request
        search_req = SearchRequest(
            query=voice_cmd.command,
            session_id=voice_cmd.session_id,
            max_results=10,
            stores=["flipkart", "amazon"],  # Try both stores for better results
            min_price=parsed.get("min_price"),
            max_price=parsed.get("max_price")
        )
        
        # Execute search
        result = await search_products(search_req)
        return result
        
    except Exception as e:
        logger.error(f"Voice search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "voice_response": "Sorry, I couldn't understand your search request."
        }

@router.get("/search/quick/{query}")
async def quick_search(query: str, max_results: int = 5):
    """
    Quick search endpoint for simple queries
    Returns top results from Flipkart only for speed
    """
    try:
        search_req = SearchRequest(
            query=query,
            max_results=max_results,
            stores=["flipkart"]
        )
        result = await search_products(search_req)
        return result
        
    except Exception as e:
        logger.error(f"Quick search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/trending")
async def get_trending_products():
    """
    Get trending products (mock endpoint for demo)
    In production, this could scrape trending sections
    """
    trending_queries = [
        "smartphone under 20000",
        "wireless earphones",
        "laptop bag",
        "running shoes",
        "bluetooth speaker"
    ]
    
    return {
        "trending_searches": trending_queries,
        "message": "Try searching for these popular items"
    }
