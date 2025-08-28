import requests
from bs4 import BeautifulSoup
import time
import logging
import random
from typing import List, Dict, Optional
import re
import json

logger = logging.getLogger(__name__)

class SimpleScraper:
    """
    Simplified scraper using requests + BeautifulSoup for better reliability
    Optimized for real-data scraping success
    """
    
    def __init__(self):
        self.session = requests.Session()
        
        # Expanded and more realistic headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua': '"Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Referer': 'https://www.google.com/'
        }
        self.session.headers.update(self.headers)
        
        # Add cookies to appear more like a regular browser
        self.session.cookies.set('visitor', f'visitor-{random.randint(100000, 999999)}', domain='.flipkart.com')
        self.session.cookies.set('session-id', f'{random.randint(100000000, 999999999)}', domain='.amazon.in')
    
    def search_flipkart_simple(self, keywords: str, min_price: Optional[int] = None, max_price: Optional[int] = None) -> List[Dict]:
        """
        Simple Flipkart search using requests - optimized for real-time data retrieval
        """
        try:
            # Enhanced search terms processing - remove command words, focus on product keywords
            search_terms = keywords.lower()
            search_terms = re.sub(r'\b(find|get|search|for|me|please|show|looking|under)\b', '', search_terms)
            
            # Extract essential product keywords
            price_pattern = r'under\s+(\d+)'
            price_match = re.search(price_pattern, search_terms)
            if price_match:
                # Remove price phrases from search terms
                search_terms = re.sub(r'under\s+\d+\s*(rupees|rs|inr)?', '', search_terms)
            
            # Clean up the search terms
            search_terms = search_terms.strip()
            search_terms = re.sub(r'\s+', ' ', search_terms)  # Normalize spaces
            search_terms = search_terms.replace(' ', '+')
            
            logger.info(f"Optimized search terms: '{search_terms}'")
            
            # Expanded user agents collection for better anti-bot evasion
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.0.0 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.91',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            self.session.headers.update({'User-Agent': random.choice(user_agents)})
            
            # Add more realistic headers and cookies
            self.session.headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.google.com/search?q=flipkart+' + search_terms.replace('+', '+'),
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'cross-site',
                'Cache-Control': 'max-age=0',
                'TE': 'trailers'
            })
            
            # Add browser-like cookies
            self.session.cookies.set('T', f'BR%3A{random.randint(1000000, 9999999)}', domain='www.flipkart.com')
            self.session.cookies.set('SN', f'VI{random.randint(10000000, 99999999)}.{int(time.time())}', domain='www.flipkart.com')
            
            # Build optimized search URL
            search_url = f"https://www.flipkart.com/search?q={search_terms}"
            if max_price:
                search_url += f"&p%5B%5D=facets.price_range.to%3D{max_price}"
            if min_price:
                search_url += f"&p%5B%5D=facets.price_range.from%3D{min_price}"
            
            logger.info(f"Simple scraping URL: {search_url}")
            
            # Make request with more robust retry mechanism
            for attempt in range(5):  # Increased retries
                try:
                    # Simulate human behavior by first visiting the homepage
                    if attempt == 0:
                        self.session.get("https://www.flipkart.com/", timeout=10)
                        time.sleep(random.uniform(1, 2))
                    
                    response = self.session.get(search_url, timeout=20)  # Increased timeout
                    
                    if response.status_code == 200:
                        if len(response.content) > 5000:  # Check for meaningful response size
                            break
                        else:
                            logger.warning("Got suspiciously small response, retrying...")
                    else:
                        logger.warning(f"Request failed with status {response.status_code}, retrying... (attempt {attempt+1}/5)")
                    
                    # Rotate user agent and referrer on retry
                    self.session.headers.update({
                        'User-Agent': random.choice(user_agents),
                        'Referer': random.choice([
                            'https://www.google.com/search?q=flipkart+products',
                            'https://www.flipkart.com/',
                            'https://www.bing.com/search?q=online+shopping'
                        ])
                    })
                    time.sleep(random.uniform(3, 7))  # Longer delay between retries
                    
                except Exception as e:
                    logger.warning(f"Request error: {e}, retrying... (attempt {attempt+1}/5)")
                    if attempt == 4:  # Last attempt
                        raise
                    time.sleep(random.uniform(4, 8))  # Even longer delay between error retries
            
            # Check if we got a valid response
            if response.status_code != 200:
                raise Exception(f"Failed to get valid response after 5 attempts. Last status code: {response.status_code}")
                
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            products = []
            
            # Look for product containers with expanded selector options
            product_selectors = [
                '[data-id]',
                '._1AtVbE',
                '._4ddWXP',
                '._13oc-S',
                '._1xHGtK',
                '._2B099V',
                '._373qXS',
                '.CXW8mj',
                '._3pLy-c',
                '.col-12-12',
                '._2kHMtA',
                '._1ssW24'
            ]
            
            product_elements = []
            for selector in product_selectors:
                elements = soup.select(selector)
                if elements and len(elements) > 3:  # Ensure we found multiple products
                    product_elements = elements[:25]  # Increased limit
                    logger.info(f"Found {len(elements)} products with selector: {selector}")
                    break
            
            if not product_elements:
                logger.warning("No product elements found with standard selectors, trying alternative approach")
                # Try to find any divs with price elements as a fallback
                price_elements = soup.select('._30jeq3')
                if price_elements:
                    logger.info(f"Found {len(price_elements)} price elements, extracting parent products")
                    for price_elem in price_elements[:25]:
                        # Go up to potential product container
                        parent = price_elem.parent
                        for _ in range(4):  # Try up to 4 levels up
                            if parent and parent.name == 'div':
                                product_elements.append(parent)
                                break
                            parent = parent.parent if parent else None
            
            # Process found products
            for element in product_elements:
                try:
                    product = self._extract_product_simple(element)
                    if product and 'title' in product and 'price' in product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"Error extracting product: {e}")
                    continue
            
            # Log summary of findings
            if products:
                logger.info(f"Simple scraper found {len(products)} real products")
                logger.debug(f"Sample product: {products[0]['title']} - ₹{products[0]['price']}")
            else:
                logger.warning("No products extracted from response")
            
            return products
            
        except Exception as e:
            logger.error(f"Simple scraping failed: {e}")
            return []
    
    def _extract_product_simple(self, element) -> Optional[Dict]:
        """Extract product from BeautifulSoup element - enhanced for better data extraction"""
        product = {}
        
        # Expanded title selectors
        title_selectors = [
            '._4rR01T',
            '.IRpwTa', 
            '.KzDlHZ',
            '._1fQZEK',
            '._2WkVRV',
            '.s1Q9rs',
            '._3wU53n',
            '.s1Q9rs',
            '._product-name',
            '.col-7-12 div',
            'a[title]',  # Sometimes title is in the a tag's title attribute
            '.row .col h1',  # Product detail page
            '._1YokD2 ._2GoDe3',
            '._2gMWsk ._2tfzpE',
            'h3',  # Generic h3 tag
            'h2'   # Generic h2 tag
        ]
        
        # Expanded price selectors
        price_selectors = [
            '._30jeq3',
            '._1_WHN1',
            '.Nx9bqj',
            '._25b18c',
            '.HjBqx_',
            '._16Jk6d',
            '._1V_ZGU',
            '.dyC3Yd ._1V_ZGU',
            '._2_B9h_ ._2p6lqe',
            '.col-7-12 ._30jeq3',
            'div[data-price]'  # Some product elements have data-price attribute
        ]
        
        # Extract title - try multiple approaches
        # 1. Try direct selectors
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem and title_elem.get_text(strip=True):
                product['title'] = title_elem.get_text(strip=True)[:100]
                break
                
        # 2. If no title found, look for title attributes in links
        if 'title' not in product:
            links = element.select('a[title]')
            for link in links:
                title = link.get('title', '').strip()
                if title and len(title) > 5:  # Ensure it's a meaningful title
                    product['title'] = title[:100]
                    break
        
        # 3. Last resort - look for any text in links that might be a title
        if 'title' not in product:
            links = element.select('a')
            for link in links:
                text = link.get_text(strip=True)
                if text and len(text) > 10 and len(text) < 100:  # Reasonably sized text
                    product['title'] = text[:100]
                    break
        
        # Extract price - try multiple approaches
        # 1. Try direct selectors
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                if '₹' in price_text:
                    # Extract numeric price
                    price_match = re.search(r'₹([\d,]+)', price_text)
                    if price_match:
                        try:
                            price = int(price_match.group(1).replace(',', ''))
                            product['price'] = price
                            break
                        except:
                            continue
        
        # 2. Try data-price attribute if available
        if 'price' not in product:
            elements_with_price = element.select('[data-price]')
            for price_elem in elements_with_price:
                try:
                    price_value = price_elem.get('data-price', '')
                    if price_value and price_value.isdigit():
                        product['price'] = int(price_value)
                        break
                except:
                    continue
                    
        # 3. General search for price patterns in all text
        if 'price' not in product:
            all_text = element.get_text(strip=True)
            price_patterns = [
                r'₹\s*([\d,]+)',  # ₹1,999
                r'Rs\.?\s*([\d,]+)',  # Rs. 1,999
                r'Price:?\s*₹\s*([\d,]+)'  # Price: ₹1,999
            ]
            
            for pattern in price_patterns:
                price_match = re.search(pattern, all_text)
                if price_match:
                    try:
                        price = int(price_match.group(1).replace(',', ''))
                        if 100 <= price <= 500000:  # Reasonable price range
                            product['price'] = price
                            break
                    except:
                        continue
        
        # Extract URL with improved handling
        link_elem = element.find('a')
        if link_elem and link_elem.get('href'):
            href = link_elem['href']
            # Ensure valid URL
            if href.startswith('/') or not href.startswith('http'):
                product['url'] = f"https://www.flipkart.com{href}" if href.startswith('/') else f"https://www.flipkart.com/{href}"
            else:
                product['url'] = href
        else:
            # Try to find any link in the element
            all_links = element.select('a')
            for link in all_links:
                href = link.get('href', '')
                if href and len(href) > 5:  # Reasonable URL length
                    if href.startswith('/') or not href.startswith('http'):
                        product['url'] = f"https://www.flipkart.com{href}" if href.startswith('/') else f"https://www.flipkart.com/{href}"
                    else:
                        product['url'] = href
                    break
            
        # Add store information
        product['store'] = 'flipkart'
        product['scraped_at'] = time.time()
        product['source'] = 'real-time-scraper'  # Mark as real data
        
        # Only return if we have both title and price
        if product.get('title') and product.get('price'):
            # Add some additional debugging
            logger.debug(f"Extracted real product: {product['title'][:30]}... - ₹{product['price']}")
            return product
        else:
            logger.debug("Failed to extract product - missing title or price")
            return None

# Global simple scraper instance
simple_scraper = SimpleScraper()

def search_with_simple_scraper(keywords: str, min_price: Optional[int] = None, max_price: Optional[int] = None) -> List[Dict]:
    """
    Use the simple scraper as a fallback
    """
    return simple_scraper.search_flipkart_simple(keywords, min_price, max_price)
