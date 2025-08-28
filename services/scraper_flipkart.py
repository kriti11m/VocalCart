from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import random
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)

class FlipkartScraper:
    """
    Enhanced Flipkart scraper for real-time product fetching
    Optimized for speed and reliability with better error handling
    """
    
    def __init__(self):
        self.base_url = "https://www.flipkart.com"
        self.driver = None
        self.session_active = False
        
    def _get_driver_options(self):
        """Configure Chrome options for optimal scraping"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")
        options.add_argument("--disable-javascript")  # Faster loading
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Randomize user agent
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        return options
    
    def _initialize_driver(self):
        """Initialize Chrome driver with improved reliability"""
        if self.session_active and self.driver:
            return self.driver
            
        options = self._get_driver_options()
        
        try:
            # Try ChromeDriverManager first
            driver_path = ChromeDriverManager().install()
            
            # Check if the driver file exists and is executable
            import os
            if os.path.exists(driver_path):
                # Make sure the driver is executable
                os.chmod(driver_path, 0o755)
                logger.info(f"Using ChromeDriver at: {driver_path}")
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            logger.info("ChromeDriverManager initialization successful")
            
        except Exception as e1:
            logger.warning(f"ChromeDriverManager failed: {e1}")
            try:
                # Try with system Chrome and chromedriver
                import shutil
                system_chromedriver = shutil.which('chromedriver')
                if system_chromedriver:
                    logger.info(f"Using system chromedriver: {system_chromedriver}")
                    service = Service(system_chromedriver)
                    self.driver = webdriver.Chrome(service=service, options=options)
                    logger.info("System ChromeDriver initialization successful")
                else:
                    # Try without specifying service
                    logger.info("Attempting initialization with default ChromeDriver")
                    self.driver = webdriver.Chrome(options=options)
                    logger.info("Default ChromeDriver initialization successful")
                    
            except Exception as e2:
                logger.error(f"All ChromeDriver methods failed: {e1}, {e2}")
                # Raise exception to notify about failure rather than silently returning None
                raise RuntimeError("Failed to initialize ChromeDriver after all attempts")
        
        if self.driver:
            self.session_active = True
            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(45)  # Increased timeout for slower connections
            logger.info("WebDriver initialized successfully")
            
        return self.driver
    
    def search(self, keywords: str, min_price: Optional[int] = None, max_price: Optional[int] = None) -> List[Dict]:
        """
        Search Flipkart for products with given criteria
        Returns list of product dictionaries
        """
        logger.info(f"Searching for: {keywords} (price range: {min_price}-{max_price})")
        
        # Try with Selenium WebDriver (real scraping)
        try:
            driver = self._initialize_driver()
            if not driver:
                logger.error("Failed to initialize Flipkart driver")
                raise Exception("WebDriver initialization failed")
                
            # Build search URL
            search_url = f"https://www.flipkart.com/search?q={keywords.replace(' ', '+')}"
            if max_price:
                search_url += f"&p%5B%5D=facets.price_range.to%3D{max_price}"
            if min_price:
                search_url += f"&p%5B%5D=facets.price_range.from%3D{min_price}"
            
            logger.info(f"Accessing: {search_url}")
            
            # Set page load timeout to prevent hanging
            driver.set_page_load_timeout(30)
            driver.get(search_url)
            
            # Handle popups
            self._handle_popups(driver)
            
            # Extract products with timeout
            import threading
            products = []
            extraction_completed = threading.Event()
            
            def extract_with_timeout():
                nonlocal products
                try:
                    products = self._extract_products(driver)
                    extraction_completed.set()
                except Exception as e:
                    logger.error(f"Extraction error: {e}")
                    extraction_completed.set()
            
            extraction_thread = threading.Thread(target=extract_with_timeout)
            extraction_thread.daemon = True
            extraction_thread.start()
            
            # Wait for extraction with timeout
            if not extraction_completed.wait(timeout=20):
                logger.warning("Product extraction timed out, trying simple scraper")
                # Try simple scraper as backup
                try:
                    simple_products = self._search_with_simple_scraper(keywords, min_price, max_price)
                    if simple_products:
                        logger.info(f"Simple scraper succeeded with {len(simple_products)} products")
                        return simple_products[:20]
                except Exception as e:
                    logger.warning(f"Simple scraper also failed: {e}")
                    # Continue with whatever Selenium got so far
            
            # Filter results by price if needed
            if products and (min_price or max_price):
                products = self._filter_by_price(products, min_price, max_price)
            
            logger.info(f"Found {len(products)} products via WebDriver")
            return products[:20]
                
        except Exception as e:
            logger.error(f"WebDriver search failed: {e}")
            # Try simple scraper for speed (with network timeout handling)
            try:
                logger.info("Trying simple scraper as fallback")
                products = self._search_with_simple_scraper(keywords, min_price, max_price)
                if products:
                    logger.info(f"Simple scraper succeeded with {len(products)} products")
                    return products[:20]
            except Exception as e2:
                logger.error(f"Simple scraper failed: {e2}")
                # We're out of options here
                logger.error("All scraping methods failed, returning empty results")
                return []
    
    def _search_with_simple_scraper(self, keywords: str, min_price: Optional[int] = None, max_price: Optional[int] = None) -> List[Dict]:
        """Use simple scraper as fallback"""
        try:
            from .simple_scraper import search_with_simple_scraper
            logger.info("Attempting real-time scraping with simple scraper")
            products = search_with_simple_scraper(keywords, min_price, max_price)
            if products:
                logger.info(f"Simple scraper found {len(products)} products")
                return products
            else:
                logger.warning("Simple scraper returned no products")
                
            # Try with custom request without dependency
            import requests
            from bs4 import BeautifulSoup
            import re
            import random
            
            # Random user agent to avoid detection
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]
            
            headers = {
                "User-Agent": random.choice(user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0"
            }
            
            search_url = f"https://www.flipkart.com/search?q={keywords.replace(' ', '+')}"
            if max_price:
                search_url += f"&p%5B%5D=facets.price_range.to%3D{max_price}"
            if min_price:
                search_url += f"&p%5B%5D=facets.price_range.from%3D{min_price}"
                
            logger.info(f"Direct request to: {search_url}")
            
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Extract products
                products = []
                product_divs = soup.select("div._1AtVbE") or soup.select("div._4ddWXP") or soup.select("div._2B099V")
                
                for div in product_divs[:20]:
                    product = {}
                    
                    # Title
                    title_elem = (div.select_one("div._4rR01T") or div.select_one("a.IRpwTa") or 
                                div.select_one("div.s1Q9rs") or div.select_one("a.s1Q9rs"))
                    if title_elem:
                        product["title"] = title_elem.text.strip()
                    
                    # Price
                    price_elem = div.select_one("div._30jeq3")
                    if price_elem:
                        price_text = price_elem.text.strip()
                        if "₹" in price_text:
                            price = ''.join(c for c in price_text if c.isdigit())
                            if price:
                                product["price"] = int(price)
                    
                    # Link
                    link_elem = div.select_one("a[href]")
                    if link_elem and link_elem.get("href"):
                        href = link_elem.get("href")
                        product["url"] = "https://www.flipkart.com" + href if not href.startswith("http") else href
                    
                    # Only add if we have title and price
                    if product.get("title") and product.get("price"):
                        product["store"] = "flipkart"
                        products.append(product)
                
                if products:
                    logger.info(f"Direct request found {len(products)} products")
                    return products
                
        except Exception as e:
            logger.error(f"All simple scraping methods failed: {e}")
        
        # No fallback to demo data - return empty list
        logger.error("All scraping methods failed, returning empty results")
        return []
    
    def _handle_popups(self, driver):
        """Handle login and other popups"""
        try:
            # Close login popup
            close_buttons = [
                "//button[text()='✕']",
                "//button[@class='_2KpZ6l _2doB4z']",
                "//span[@class='_30XB9F']",
                "//button[contains(@class, 'close')]"
            ]
            
            for button_xpath in close_buttons:
                try:
                    close_btn = driver.find_element(By.XPATH, button_xpath)
                    close_btn.click()
                    time.sleep(1)
                    break
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Popup handling: {e}")
    
    def _extract_products(self, driver) -> List[Dict]:
        """Extract product information using multiple strategies"""
        products = []
        
        # Multiple product container selectors
        container_selectors = [
            "div[data-id]",
            "div._1AtVbE",
            "div._4ddWXP", 
            "div._1fQZEK",
            "div._13oc-S",
            "div._3pLy-c"
        ]
        
        product_elements = []
        for selector in container_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    product_elements = elements
                    logger.debug(f"Found {len(elements)} products with selector: {selector}")
                    break
            except:
                continue
        
        # Extract product details
        for element in product_elements[:25]:  # Process first 25 elements
            try:
                product = self._extract_single_product(element)
                if product and product.get('title') and product.get('price'):
                    products.append(product)
            except Exception as e:
                logger.debug(f"Error extracting single product: {e}")
                continue
        
        return products
    
    def _extract_single_product(self, element) -> Optional[Dict]:
        """Extract details from a single product element"""
        product = {}
        
        # Title selectors
        title_selectors = [
            "div._4rR01T",
            "a.IRpwTa",
            "div.KzDlHZ", 
            "a._1fQZEK",
            "div._2WkVRV",
            "a.s1Q9rs",
            "div._3wU53n"
        ]
        
        # Price selectors
        price_selectors = [
            "div._30jeq3",
            "div._1_WHN1", 
            "div.Nx9bqj",
            "div._25b18c",
            "span._1_WHN1",
            "div._3I9_wc"
        ]
        
        # Extract title
        for selector in title_selectors:
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, selector)
                title = title_elem.text.strip()
                if title:
                    product['title'] = title[:100]  # Limit title length
                    break
            except:
                continue
        
        # Extract price
        for selector in price_selectors:
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, selector)
                price_text = price_elem.text.strip()
                if price_text and '₹' in price_text:
                    # Clean price text
                    price_clean = price_text.replace("₹", "").replace(",", "").split()[0]
                    price = int(price_clean)
                    product['price'] = price
                    break
            except:
                continue
        
        # Try to extract URL
        try:
            link_elem = element.find_element(By.TAG_NAME, "a")
            href = link_elem.get_attribute("href")
            if href:
                product['url'] = href if href.startswith('http') else f"{self.base_url}{href}"
        except:
            product['url'] = f"{self.base_url}/search"
        
        # Add store info
        product['store'] = 'flipkart'
        product['scraped_at'] = time.time()
        
        return product if product.get('title') and product.get('price') else None
    
    def _filter_by_price(self, products: List[Dict], min_price: Optional[int], max_price: Optional[int]) -> List[Dict]:
        """Filter products by price range"""
        if not min_price and not max_price:
            return products
        
        filtered = []
        for product in products:
            price = product.get('price', 0)
            if min_price and price < min_price:
                continue
            if max_price and price > max_price:
                continue
            filtered.append(product)
        
        return filtered
    
    def _get_realistic_demo_products(self, keywords: str, min_price: Optional[int] = None, max_price: Optional[int] = None) -> List[Dict]:
        """Generate realistic demo products based on search keywords"""
        import random
        
        # Product templates for different categories
        product_templates = {
            'shoes': [
                {'name': 'Nike Air Max 270 Running Shoes', 'brand': 'Nike', 'base_price': 7999},
                {'name': 'Adidas Ultraboost 22 Running Shoes', 'brand': 'Adidas', 'base_price': 12999},
                {'name': 'Puma Future Rider Play On Sneakers', 'brand': 'Puma', 'base_price': 4499},
                {'name': 'Reebok Classic Leather Casual Shoes', 'brand': 'Reebok', 'base_price': 3999},
                {'name': 'Converse Chuck Taylor All Star Sneakers', 'brand': 'Converse', 'base_price': 2999}
            ],
            'phone': [
                {'name': 'iPhone 15 Pro Max', 'brand': 'Apple', 'base_price': 159900},
                {'name': 'Samsung Galaxy S24 Ultra', 'brand': 'Samsung', 'base_price': 124999},
                {'name': 'OnePlus 12 5G', 'brand': 'OnePlus', 'base_price': 64999},
                {'name': 'Google Pixel 8 Pro', 'brand': 'Google', 'base_price': 106999},
                {'name': 'Xiaomi 14 Ultra', 'brand': 'Xiaomi', 'base_price': 79999}
            ],
            'laptop': [
                {'name': 'MacBook Pro 16-inch M3 Pro', 'brand': 'Apple', 'base_price': 249900},
                {'name': 'Dell XPS 13 Plus', 'brand': 'Dell', 'base_price': 129999},
                {'name': 'HP Spectre x360 14', 'brand': 'HP', 'base_price': 119999},
                {'name': 'Lenovo ThinkPad X1 Carbon', 'brand': 'Lenovo', 'base_price': 164999},
                {'name': 'ASUS ZenBook Pro 16X', 'brand': 'ASUS', 'base_price': 199999}
            ]
        }
        
        # Find matching category
        keywords_lower = keywords.lower()
        matching_category = 'phone'  # Default
        
        for category in product_templates:
            if category in keywords_lower:
                matching_category = category
                break
        
        # Check for common keywords
        if any(word in keywords_lower for word in ['mobile', 'smartphone', 'iphone', 'samsung']):
            matching_category = 'phone'
        elif any(word in keywords_lower for word in ['computer', 'macbook', 'gaming']):
            matching_category = 'laptop'
        
        templates = product_templates[matching_category]
        products = []
        
        for i, template in enumerate(templates):
            # Apply price variation
            base_price = template['base_price']
            current_price = int(base_price * random.uniform(0.85, 1.15))
            
            # Apply discount
            discount_percent = random.randint(10, 35)
            original_price = int(current_price / (1 - discount_percent/100))
            
            # Filter by price range
            if min_price and current_price < min_price:
                continue
            if max_price and current_price > max_price:
                continue
            
            product = {
                'name': template['name'],
                'price': f"₹{current_price:,}",
                'original_price': f"₹{original_price:,}",
                'discount': f"{discount_percent}% off",
                'rating': round(random.uniform(4.0, 4.7), 1),
                'reviews': f"{random.randint(100, 2000):,} reviews",
                'brand': template['brand'],
                'url': f"https://www.flipkart.com/product-{i+1}",
                'image': f"https://via.placeholder.com/300x300?text={template['brand']}",
                'availability': 'In Stock',
                'delivery': 'Free Delivery',
                'source': 'Flipkart (Enhanced Demo)',
                'description': f"Premium {template['name']} with latest features"
            }
            
            products.append(product)
        
        logger.info(f"Generated {len(products)} enhanced demo products for '{keywords}'")
        return products

    def _get_fallback_products(self, keywords: str) -> List[Dict]:
        """Return sample products when scraping fails"""
        logger.info("Returning fallback products for demo")
        
        # Generate realistic sample products based on keywords
        sample_products = []
        base_keywords = keywords.lower().split()
        
        if any(word in base_keywords for word in ['shoes', 'shoe']):
            sample_products = [
                {"title": "Nike Air Max Running Shoes", "price": 2499, "store": "flipkart", "url": "https://flipkart.com/sample"},
                {"title": "Adidas Ultraboost Sneakers", "price": 1899, "store": "flipkart", "url": "https://flipkart.com/sample"},
                {"title": "Puma Sports Shoes Black", "price": 1599, "store": "flipkart", "url": "https://flipkart.com/sample"}
            ]
        elif any(word in base_keywords for word in ['phone', 'mobile']):
            sample_products = [
                {"title": "Samsung Galaxy A54 5G", "price": 25999, "store": "flipkart", "url": "https://flipkart.com/sample"},
                {"title": "Xiaomi Redmi Note 12", "price": 15999, "store": "flipkart", "url": "https://flipkart.com/sample"},
                {"title": "OnePlus Nord CE 3", "price": 22999, "store": "flipkart", "url": "https://flipkart.com/sample"}
            ]
        else:
            # Generic products
            sample_products = [
                {"title": f"{keywords.title()} - Premium Quality", "price": 1299, "store": "flipkart", "url": "https://flipkart.com/sample"},
                {"title": f"Best {keywords.title()} Deal", "price": 999, "store": "flipkart", "url": "https://flipkart.com/sample"},
                {"title": f"Top Rated {keywords.title()}", "price": 1599, "store": "flipkart", "url": "https://flipkart.com/sample"}
            ]
        
        return sample_products
    
    def close(self):
        """Close the driver session"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            finally:
                self.driver = None
                self.session_active = False
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()
