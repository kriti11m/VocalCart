from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import random
from typing import List, Dict, Optional
import re

logger = logging.getLogger(__name__)

class AmazonScraper:
    """
    Amazon scraper for real-time product fetching
    Note: Amazon has stricter anti-bot measures, so this includes more robust evasion
    """
    
    def __init__(self):
        self.base_url = "https://www.amazon.in"
        self.driver = None
        self.session_active = False
        
    def _get_driver_options(self):
        """Configure Chrome options for Amazon scraping"""
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
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # More realistic user agents for Amazon
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")
        
        # Additional headers for better stealth
        options.add_argument("--accept-language=en-US,en;q=0.9")
        options.add_argument("--accept-encoding=gzip, deflate, br")
        
        return options
    
    def _initialize_driver(self):
        """Initialize Chrome driver for Amazon"""
        if self.session_active and self.driver:
            return self.driver
            
        options = self._get_driver_options()
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e1:
            logger.warning(f"ChromeDriverManager failed: {e1}")
            try:
                options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                service = Service()
                self.driver = webdriver.Chrome(service=service, options=options)
            except Exception as e2:
                logger.warning(f"System Chrome failed: {e2}")
                self.driver = webdriver.Chrome(options=options)
        
        if self.driver:
            self.session_active = True
            self.driver.implicitly_wait(10)
            
            # Execute stealth script
            stealth_script = """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            """
            self.driver.execute_script(stealth_script)
            
        return self.driver
    
    def search(self, keywords: str, min_price: Optional[int] = None, max_price: Optional[int] = None) -> List[Dict]:
        """
        Search Amazon for products with given criteria - REAL DATA ONLY
        """
        products = []
        
        try:
            driver = self._initialize_driver()
            if not driver:
                logger.error("Failed to initialize Amazon driver")
                return []  # Return empty list instead of fallback products
            
            # Build Amazon search URL
            search_url = f"{self.base_url}/s?k={keywords.replace(' ', '+')}"
            
            # Add price filters if specified
            if min_price or max_price:
                # Amazon price filter format
                if min_price:
                    search_url += f"&rh=p_36%3A{min_price * 100}-"
                if max_price:
                    search_url += f"{max_price * 100}"
            
            logger.info(f"Scraping Amazon URL: {search_url}")
            
            # Navigate with delay to appear human-like
            driver.get(search_url)
            time.sleep(random.uniform(3, 5))
            
            # Handle any captcha or bot detection
            if self._check_for_captcha(driver):
                logger.warning("Amazon captcha detected - cannot proceed with scraping")
                return []  # Return empty results instead of fallback
            
            # Scroll gradually to load content
            self._gradual_scroll(driver)
            
            # Extract products
            products = self._extract_amazon_products(driver)
            
            # Filter by price if needed
            if min_price or max_price:
                products = self._filter_by_price(products, min_price, max_price)
            
            logger.info(f"Successfully scraped {len(products)} products from Amazon")
            
        except Exception as e:
            logger.error(f"Amazon scraping error: {e}")
            # No fallback to dummy products - return empty list
            return []
        
        return products[:15]  # Limit Amazon results
    
    def _check_for_captcha(self, driver) -> bool:
        """Check if Amazon is showing captcha or bot detection"""
        try:
            # Check for common Amazon anti-bot elements
            captcha_indicators = [
                "captcha",
                "robot",
                "automated",
                "verify you are human"
            ]
            
            page_text = driver.page_source.lower()
            return any(indicator in page_text for indicator in captcha_indicators)
            
        except:
            return False
    
    def _gradual_scroll(self, driver):
        """Scroll gradually to appear more human-like"""
        try:
            # Scroll in small increments
            total_height = driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            scroll_increment = total_height // 4
            
            for _ in range(3):
                current_position += scroll_increment
                driver.execute_script(f"window.scrollTo(0, {current_position});")
                time.sleep(random.uniform(1, 2))
                
        except Exception as e:
            logger.debug(f"Scroll error: {e}")
    
    def _extract_amazon_products(self, driver) -> List[Dict]:
        """Extract products from Amazon search results"""
        products = []
        
        # Amazon product container selectors
        container_selectors = [
            '[data-component-type="s-search-result"]',
            '.s-result-item',
            '[data-asin]',
            '.sg-col-inner .s-widget-container'
        ]
        
        product_elements = []
        for selector in container_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    product_elements = elements
                    logger.debug(f"Found {len(elements)} Amazon products with selector: {selector}")
                    break
            except:
                continue
        
        # Extract product details
        for element in product_elements[:20]:
            try:
                product = self._extract_single_amazon_product(element)
                if product and product.get('title') and product.get('price'):
                    products.append(product)
            except Exception as e:
                logger.debug(f"Error extracting Amazon product: {e}")
                continue
        
        return products
    
    def _extract_single_amazon_product(self, element) -> Optional[Dict]:
        """Extract details from a single Amazon product element"""
        product = {}
        
        # Title selectors for Amazon
        title_selectors = [
            'h2 a span',
            '.s-size-mini .s-link-style a .s-color-base',
            'h2 .s-color-base',
            '.s-title-instructions-style h2 a span'
        ]
        
        # Price selectors for Amazon
        price_selectors = [
            '.a-price-whole',
            '.a-price .a-offscreen',
            '.a-price-range .a-offscreen',
            '.s-price-instructions-style .a-price .a-offscreen'
        ]
        
        # Extract title
        for selector in title_selectors:
            try:
                title_elem = element.find_element(By.CSS_SELECTOR, selector)
                title = title_elem.text.strip()
                if title:
                    product['title'] = title[:100]
                    break
            except:
                continue
        
        # Extract price
        for selector in price_selectors:
            try:
                price_elem = element.find_element(By.CSS_SELECTOR, selector)
                price_text = price_elem.text.strip()
                if price_text:
                    # Clean Amazon price text (handles ₹, commas, etc.)
                    price_match = re.search(r'[\d,]+', price_text.replace(',', ''))
                    if price_match:
                        price = int(price_match.group().replace(',', ''))
                        product['price'] = price
                        break
            except:
                continue
        
        # Extract URL
        try:
            link_elem = element.find_element(By.CSS_SELECTOR, 'h2 a')
            href = link_elem.get_attribute("href")
            if href:
                product['url'] = href if href.startswith('http') else f"{self.base_url}{href}"
        except:
            product['url'] = f"{self.base_url}/s"
        
        # Extract rating (optional)
        try:
            rating_elem = element.find_element(By.CSS_SELECTOR, '.a-icon-alt')
            rating_text = rating_elem.get_attribute('innerHTML')
            if rating_text and 'out of' in rating_text:
                rating_match = re.search(r'(\d+\.?\d*) out of', rating_text)
                if rating_match:
                    product['rating'] = float(rating_match.group(1))
        except:
            pass
        
        # Add store info
        product['store'] = 'amazon'
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
    
    def _get_fallback_products(self, keywords: str) -> List[Dict]:
        """Return sample Amazon products when scraping fails"""
        logger.info("Returning Amazon fallback products")
        
        base_keywords = keywords.lower().split()
        sample_products = []
        
        if any(word in base_keywords for word in ['shoes', 'shoe']):
            sample_products = [
                {"title": "Nike Revolution 6 Running Shoes", "price": 2799, "store": "amazon", "url": "https://amazon.in/sample", "rating": 4.2},
                {"title": "Adidas Lite Racer Adapt Sneakers", "price": 2199, "store": "amazon", "url": "https://amazon.in/sample", "rating": 4.0},
                {"title": "Puma Anzarun Lite Sports Shoes", "price": 1899, "store": "amazon", "url": "https://amazon.in/sample", "rating": 4.1}
            ]
        elif any(word in base_keywords for word in ['phone', 'mobile']):
            sample_products = [
                {"title": "Samsung Galaxy M14 5G", "price": 16999, "store": "amazon", "url": "https://amazon.in/sample", "rating": 4.3},
                {"title": "Xiaomi Redmi 12C", "price": 8999, "store": "amazon", "url": "https://amazon.in/sample", "rating": 4.1},
                {"title": "Realme C55", "price": 12999, "store": "amazon", "url": "https://amazon.in/sample", "rating": 4.2}
            ]
        else:
            sample_products = [
                {"title": f"Amazon Choice {keywords.title()}", "price": 1599, "store": "amazon", "url": "https://amazon.in/sample", "rating": 4.0},
                {"title": f"Best Seller {keywords.title()}", "price": 1299, "store": "amazon", "url": "https://amazon.in/sample", "rating": 4.2},
                {"title": f"Premium {keywords.title()}", "price": 1999, "store": "amazon", "url": "https://amazon.in/sample", "rating": 4.1}
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
