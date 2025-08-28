"""
Simple Scraper Fallback
A fallback scraper that uses only requests/BeautifulSoup without Selenium
"""
import requests
from bs4 import BeautifulSoup
import time
import random
import logging
import re
from typing import List, Dict, Optional, Any
import json
import os

logger = logging.getLogger(__name__)

class SimpleRequestsScraper:
    """
    Ultra-simple requests-based scraper that doesn't require Selenium
    """
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.91',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        self.rotate_user_agent()
        
    def rotate_user_agent(self):
        """Rotate user agent to avoid detection"""
        user_agent = random.choice(self.user_agents)
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'Upgrade-Insecure-Requests': '1'
        })
        return user_agent
        
    def search_flipkart(self, keywords: str, min_price: Optional[int] = None, max_price: Optional[int] = None) -> List[Dict]:
        """Search Flipkart for products"""
        try:
            # Clean up search terms
            search_terms = keywords.lower()
            search_terms = re.sub(r'\b(find|get|search|for|me|please|show|looking|under)\b', '', search_terms)
            search_terms = search_terms.strip()
            search_terms = re.sub(r'\s+', ' ', search_terms)
            search_terms = search_terms.replace(' ', '+')
            
            logger.info(f"Simple scraper searching for: {search_terms}")
            
            # Build search URL
            search_url = f"https://www.flipkart.com/search?q={search_terms}"
            if max_price:
                search_url += f"&p%5B%5D=facets.price_range.to%3D{max_price}"
            if min_price:
                search_url += f"&p%5B%5D=facets.price_range.from%3D{min_price}"
            
            # Make request with retry
            ua = self.rotate_user_agent()
            logger.info(f"Making request to {search_url} with UA: {ua[:30]}...")
            
            response = None
            for attempt in range(3):
                try:
                    response = self.session.get(search_url, timeout=15)
                    if response.status_code == 200:
                        break
                    self.rotate_user_agent()
                    time.sleep(random.uniform(1, 3))
                except Exception as e:
                    logger.warning(f"Request failed (attempt {attempt+1}/3): {e}")
                    self.rotate_user_agent()
                    time.sleep(random.uniform(2, 5))
            
            if not response or response.status_code != 200:
                logger.error(f"Failed to get response after 3 attempts")
                return []
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Try multiple selectors for product containers
            product_containers = []
            selectors = [
                'div._1AtVbE', 'div._4ddWXP', 'div._1xHGtK', 'div._2kHMtA',
                'div._13oc-S', 'div._3pLy-c', 'div[data-id]', 'div.CXW8mj'
            ]
            
            for selector in selectors:
                containers = soup.select(selector)
                if containers and len(containers) > 3:
                    product_containers = containers[:20]
                    logger.info(f"Found {len(containers)} products with selector: {selector}")
                    break
            
            # Extract product data
            for container in product_containers:
                product = self._extract_product(container)
                if product:
                    products.append(product)
            
            logger.info(f"Simple scraper extracted {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Simple scraper error: {e}")
            return []
    
    def _extract_product(self, element) -> Optional[Dict]:
        """Extract product data from HTML element"""
        product = {"store": "flipkart", "scraped_at": time.time()}
        
        # Extract title
        title_selectors = [
            'div._4rR01T', 'a.IRpwTa', 'a.s1Q9rs', 'div.s1Q9rs',
            'div._2WkVRV', 'div.KzDlHZ', 'a._1fQZEK'
        ]
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem and title_elem.text.strip():
                product['title'] = title_elem.text.strip()[:100]
                break
        
        # Try links with title attribute if no title found
        if 'title' not in product:
            links = element.select('a[title]')
            for link in links:
                title = link.get('title', '').strip()
                if title:
                    product['title'] = title[:100]
                    break
        
        # Extract price
        price_selectors = [
            'div._30jeq3', 'div._1_WHN1', 'div.HjBqx_',
            'div._16Jk6d', 'div._25b18c'
        ]
        
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.text.strip()
                if '₹' in price_text:
                    price_match = re.search(r'₹([\d,]+)', price_text)
                    if price_match:
                        try:
                            price = int(price_match.group(1).replace(',', ''))
                            product['price'] = price
                            break
                        except:
                            continue
        
        # Extract URL
        link_elem = element.find('a')
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            if href.startswith('/'):
                product['url'] = f"https://www.flipkart.com{href}"
            elif not href.startswith('http'):
                product['url'] = f"https://www.flipkart.com/{href}"
            else:
                product['url'] = href
        
        # Extract image
        img_elem = element.select_one('img')
        if img_elem and img_elem.get('src'):
            product['image_url'] = img_elem['src']
        
        # Only return if we have title and price
        if product.get('title') and product.get('price'):
            return product
        return None
    
    def search_amazon(self, keywords: str, min_price: Optional[int] = None, max_price: Optional[int] = None) -> List[Dict]:
        """Search Amazon for products"""
        try:
            # Clean up search terms
            search_terms = keywords.lower()
            search_terms = re.sub(r'\b(find|get|search|for|me|please|show|looking|under)\b', '', search_terms)
            search_terms = search_terms.strip()
            search_terms = re.sub(r'\s+', ' ', search_terms)
            search_terms = search_terms.replace(' ', '+')
            
            logger.info(f"Simple scraper searching Amazon for: {search_terms}")
            
            # Build search URL
            search_url = f"https://www.amazon.in/s?k={search_terms}"
            
            # Make request with retry
            ua = self.rotate_user_agent()
            logger.info(f"Making request to {search_url} with UA: {ua[:30]}...")
            
            response = None
            for attempt in range(3):
                try:
                    response = self.session.get(search_url, timeout=15)
                    if response.status_code == 200:
                        break
                    self.rotate_user_agent()
                    time.sleep(random.uniform(1, 3))
                except Exception as e:
                    logger.warning(f"Amazon request failed (attempt {attempt+1}/3): {e}")
                    self.rotate_user_agent()
                    time.sleep(random.uniform(2, 5))
            
            if not response or response.status_code != 200:
                logger.error(f"Failed to get Amazon response after 3 attempts")
                return []
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Try multiple selectors for product containers
            product_containers = []
            selectors = [
                'div.s-result-item[data-component-type="s-search-result"]',
                'div.sg-col-4-of-12',
                'div.sg-col-4-of-24',
                'div.s-asin'
            ]
            
            for selector in selectors:
                containers = soup.select(selector)
                if containers and len(containers) > 3:
                    product_containers = containers[:20]
                    logger.info(f"Found {len(containers)} Amazon products with selector: {selector}")
                    break
            
            # Extract product data
            for container in product_containers:
                product = self._extract_amazon_product(container)
                if product:
                    if min_price and product.get('price', 0) < min_price:
                        continue
                    if max_price and product.get('price', 0) > max_price:
                        continue
                    products.append(product)
            
            logger.info(f"Simple scraper extracted {len(products)} Amazon products")
            return products
            
        except Exception as e:
            logger.error(f"Amazon scraper error: {e}")
            return []
    
    def _extract_amazon_product(self, element) -> Optional[Dict]:
        """Extract Amazon product data from HTML element"""
        product = {"store": "amazon", "scraped_at": time.time()}
        
        try:
            # Extract title
            title_elem = element.select_one('h2 a span') or element.select_one('.a-text-normal')
            if title_elem:
                product['title'] = title_elem.text.strip()[:100]
            
            # Extract price
            price_elem = element.select_one('.a-price .a-offscreen') or element.select_one('.a-price-whole')
            if price_elem:
                price_text = price_elem.text.strip()
                price_match = re.search(r'(?:₹|Rs\.?|INR)?\s*([\d,]+)', price_text)
                if price_match:
                    try:
                        price = int(price_match.group(1).replace(',', ''))
                        product['price'] = price
                    except:
                        pass
            
            # Extract URL
            link_elem = element.select_one('h2 a') or element.select_one('.a-link-normal.a-text-normal')
            if link_elem and link_elem.get('href'):
                href = link_elem['href']
                if href.startswith('/'):
                    product['url'] = f"https://www.amazon.in{href}"
                elif not href.startswith('http'):
                    product['url'] = f"https://www.amazon.in/{href}"
                else:
                    product['url'] = href
            
            # Extract image
            img_elem = element.select_one('img.s-image')
            if img_elem and img_elem.get('src'):
                product['image_url'] = img_elem['src']
            
            # Only return if we have title and price
            if product.get('title') and product.get('price'):
                return product
        except Exception as e:
            logger.debug(f"Error extracting Amazon product: {e}")
        
        return None

class NoSeleniumMultiStoreScraper:
    """Multi-store scraper that doesn't require Selenium"""
    
    def __init__(self):
        self.scraper = SimpleRequestsScraper()
        self.stores = ["flipkart", "amazon"]
    
    def search_all_stores(self, keywords: str, min_price: Optional[int] = None, max_price: Optional[int] = None) -> Dict[str, Any]:
        """Search all configured stores"""
        all_products = []
        results_by_store = {}
        
        # Search each store
        for store in self.stores:
            products = []
            
            if store == "flipkart":
                products = self.scraper.search_flipkart(keywords, min_price, max_price)
            elif store == "amazon":
                products = self.scraper.search_amazon(keywords, min_price, max_price)
            
            results_by_store[store] = products
            all_products.extend(products)
        
        # Sort by price
        all_products.sort(key=lambda x: x.get('price', 9999999))
        
        # Remove duplicates based on title similarity
        unique_products = []
        titles_seen = set()
        
        for product in all_products:
            title = product.get('title', '').lower()
            # Create a simplified title for comparison
            simple_title = re.sub(r'[^a-z0-9 ]', '', title)
            simple_title = ' '.join(simple_title.split()[:5])  # First 5 words
            
            if simple_title not in titles_seen:
                titles_seen.add(simple_title)
                unique_products.append(product)
        
        return {
            "combined_products": unique_products,
            "store_products": results_by_store,
            "total_found": len(unique_products)
        }

# Global instance for direct imports
simple_scraper = SimpleRequestsScraper()
multi_store_scraper = NoSeleniumMultiStoreScraper()

def search_flipkart_simple(keywords, min_price=None, max_price=None):
    """Search Flipkart using simple scraper"""
    return simple_scraper.search_flipkart(keywords, min_price, max_price)

def search_all_stores_simple(keywords, min_price=None, max_price=None):
    """Search all stores using simple scraper"""
    return multi_store_scraper.search_all_stores(keywords, min_price, max_price)
