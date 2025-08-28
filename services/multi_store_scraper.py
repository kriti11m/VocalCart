import asyncio
import logging
import threading
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
import time

from .scraper_flipkart import FlipkartScraper
from .scraper_amazon import AmazonScraper

logger = logging.getLogger(__name__)

class MultiStoreScraper:
    """
    Coordinator for scraping multiple e-commerce stores concurrently
    Manages scraping from Flipkart, Amazon, and potentially other stores
    """
    
    def __init__(self):
        self.stores = {
            'flipkart': FlipkartScraper(),
            'amazon': AmazonScraper()
        }
        self.executor = ThreadPoolExecutor(max_workers=3)
        
    async def search_all_stores(self, keywords: str, min_price: Optional[int] = None, 
                               max_price: Optional[int] = None, stores: Optional[List[str]] = None) -> Dict:
        """
        Search across multiple stores concurrently
        Returns combined results with store attribution
        """
        if stores is None:
            stores = ['flipkart']  # Default to just Flipkart for better reliability
        
        # Validate store names
        valid_stores = [store for store in stores if store in self.stores]
        if not valid_stores:
            logger.warning("No valid stores specified, defaulting to Flipkart")
            valid_stores = ['flipkart']
        
        logger.info(f"Searching across stores: {valid_stores}")
        
        # Create concurrent tasks with proper timeout handling
        tasks = []
        store_futures = {}
        
        # Use a thread pool with timeout for each store
        loop = asyncio.get_running_loop()
        
        for store_name in valid_stores:
            scraper = self.stores[store_name]
            
            # Create a future that will be set with the result or timeout
            future = loop.create_future()
            store_futures[store_name] = future
            
            # Start the search in a separate thread
            def search_store(store_scraper, store_name, kw, min_p, max_p, fut):
                try:
                    result = store_scraper.search(kw, min_p, max_p)
                    if not fut.done():
                        loop.call_soon_threadsafe(fut.set_result, (store_name, result))
                except Exception as e:
                    if not fut.done():
                        loop.call_soon_threadsafe(fut.set_exception, e)
            
            # Start the thread
            thread = threading.Thread(
                target=search_store,
                args=(scraper, store_name, keywords, min_price, max_price, future)
            )
            thread.daemon = True
            thread.start()
            
            # Add the future to tasks
            tasks.append(future)
        
        # Execute all tasks and collect results with retry mechanism
        results = {}
        all_products = []
        
        for store_name, task in tasks:
            # Try up to 3 times for each store
            for attempt in range(3):
                try:
                    products = await task
                    if products:  # Only consider success if we got products
                        results[store_name] = {
                            'products': products,
                            'count': len(products),
                            'status': 'success',
                            'source': 'real-time'
                        }
                        all_products.extend(products)
                        logger.info(f"Got {len(products)} products from {store_name}")
                        break  # Break retry loop on success
                    else:
                        logger.warning(f"No products returned from {store_name} (attempt {attempt+1}/3)")
                        if attempt < 2:  # Only retry if not the last attempt
                            # Create a new scraper instance for next attempt
                            scraper = self.stores[store_name]
                            task = asyncio.create_task(
                                asyncio.get_event_loop().run_in_executor(
                                    self.executor,
                                    scraper.search,
                                    keywords,
                                    min_price,
                                    max_price
                                )
                            )
                            await asyncio.sleep(2)  # Brief delay before retry
                        elif attempt == 2:  # Last attempt failed
                            results[store_name] = {
                                'products': [],
                                'count': 0,
                                'status': 'error',
                                'error': 'No products found after multiple attempts'
                            }
                            
                except Exception as e:
                    logger.error(f"Error scraping {store_name} (attempt {attempt+1}/3): {e}")
                    if attempt < 2:  # Only retry if not the last attempt
                        # Create a new scraper instance for next attempt
                        scraper = self.stores[store_name]
                        task = asyncio.create_task(
                            asyncio.get_event_loop().run_in_executor(
                                self.executor,
                                scraper.search,
                                keywords,
                                min_price,
                                max_price
                            )
                        )
                        await asyncio.sleep(2)  # Brief delay before retry
                    elif attempt == 2:  # Last attempt failed
                        results[store_name] = {
                            'products': [],
                            'count': 0,
                            'status': 'error',
                            'error': str(e)
                        }
        
        # Sort combined results by relevance/price
        sorted_products = self._sort_products(all_products)
        
        return {
            'combined_products': sorted_products,
            'total_products': len(all_products),
            'store_results': results,
            'search_query': keywords,
            'price_range': {
                'min': min_price,
                'max': max_price
            },
            'scraped_at': time.time()
        }
    
    async def search_single_store(self, store_name: str, keywords: str, 
                                 min_price: Optional[int] = None, max_price: Optional[int] = None) -> Dict:
        """
        Search a single store asynchronously
        """
        if store_name not in self.stores:
            raise ValueError(f"Store '{store_name}' not supported. Available stores: {list(self.stores.keys())}")
        
        scraper = self.stores[store_name]
        
        try:
            products = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                scraper.search,
                keywords,
                min_price,
                max_price
            )
            
            return {
                'store': store_name,
                'products': products,
                'count': len(products),
                'status': 'success',
                'search_query': keywords,
                'scraped_at': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error scraping {store_name}: {e}")
            return {
                'store': store_name,
                'products': [],
                'count': 0,
                'status': 'error',
                'error': str(e),
                'search_query': keywords
            }
    
    def _sort_products(self, products: List[Dict]) -> List[Dict]:
        """
        Sort products by relevance and price
        Priority: price (ascending), then by store preference
        """
        store_priority = {'flipkart': 1, 'amazon': 2}
        
        def sort_key(product):
            price = product.get('price', float('inf'))
            store = product.get('store', 'unknown')
            store_rank = store_priority.get(store, 999)
            return (price, store_rank)
        
        return sorted(products, key=sort_key)
    
    def get_price_comparison(self, products: List[Dict]) -> Dict:
        """
        Generate price comparison across stores for similar products
        """
        if not products:
            return {}
        
        store_stats = {}
        for product in products:
            store = product.get('store', 'unknown')
            price = product.get('price', 0)
            
            if store not in store_stats:
                store_stats[store] = {
                    'prices': [],
                    'products': [],
                    'count': 0
                }
            
            store_stats[store]['prices'].append(price)
            store_stats[store]['products'].append(product)
            store_stats[store]['count'] += 1
        
        # Calculate statistics
        comparison = {}
        for store, stats in store_stats.items():
            prices = stats['prices']
            comparison[store] = {
                'count': stats['count'],
                'min_price': min(prices) if prices else 0,
                'max_price': max(prices) if prices else 0,
                'avg_price': sum(prices) / len(prices) if prices else 0,
                'sample_products': stats['products'][:3]  # First 3 products
            }
        
        return comparison
    
    def filter_by_criteria(self, products: List[Dict], **criteria) -> List[Dict]:
        """
        Filter products by various criteria
        """
        filtered = products.copy()
        
        # Price range filtering
        min_price = criteria.get('min_price')
        max_price = criteria.get('max_price')
        if min_price or max_price:
            filtered = [
                p for p in filtered 
                if (not min_price or p.get('price', 0) >= min_price) and
                   (not max_price or p.get('price', 0) <= max_price)
            ]
        
        # Store filtering
        stores = criteria.get('stores', [])
        if stores:
            filtered = [p for p in filtered if p.get('store') in stores]
        
        # Rating filtering
        min_rating = criteria.get('min_rating')
        if min_rating:
            filtered = [p for p in filtered if p.get('rating', 0) >= min_rating]
        
        # Keyword filtering
        keywords = criteria.get('keywords', [])
        if keywords:
            keywords_lower = [k.lower() for k in keywords]
            filtered = [
                p for p in filtered 
                if any(keyword in p.get('title', '').lower() for keyword in keywords_lower)
            ]
        
        return filtered
    
    def get_best_deals(self, products: List[Dict], limit: int = 5) -> List[Dict]:
        """
        Get best deals based on price and ratings
        """
        if not products:
            return []
        
        # Score products based on price (lower is better) and rating (higher is better)
        scored_products = []
        
        max_price = max(p.get('price', 0) for p in products) or 1
        
        for product in products:
            price = product.get('price', 0)
            rating = product.get('rating', 3.0)  # Default rating
            
            # Normalize price (0-1, lower is better)
            price_score = 1 - (price / max_price)
            
            # Normalize rating (0-1, higher is better)
            rating_score = rating / 5.0
            
            # Combined score (weighted: 60% price, 40% rating)
            combined_score = (price_score * 0.6) + (rating_score * 0.4)
            
            scored_products.append((combined_score, product))
        
        # Sort by score (descending) and return top deals
        scored_products.sort(reverse=True)
        return [product for score, product in scored_products[:limit]]
    
    def close_all(self):
        """Close all scraper sessions"""
        for scraper in self.stores.values():
            try:
                scraper.close()
            except:
                pass
    
    def __del__(self):
        """Cleanup on destruction"""
        self.close_all()
