from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging
import asyncio
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus
import re
from typing import List, Dict, Any
import json

class MultiStoreScraper:
    def __init__(self):
        self.setup_driver_options()
        
    def setup_driver_options(self):
        """Setup Chrome driver options for scraping"""
        self.options = ChromeOptions()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        
    def _create_driver(self):
        """Create Chrome WebDriver with optimized settings and ARM64 compatibility"""
        try:
            options = ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')
            options.add_argument('--disable-javascript')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Handle macOS ARM64 ChromeDriver issues
            try:
                # Try with ChromeDriverManager first
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            except Exception as e1:
                logging.warning(f"ChromeDriverManager failed: {e1}, trying system Chrome")
                try:
                    # Try using system Chrome if available
                    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                    driver = webdriver.Chrome(options=options)
                except Exception as e2:
                    logging.error(f"System Chrome also failed: {e2}")
                    return None
            
            # Set timeouts
            driver.set_page_load_timeout(10)
            driver.implicitly_wait(3)
            
            return driver
            
        except Exception as e:
            logging.error(f"Failed to create driver: {e}")
            return None

    def scrape_flipkart(self, query, min_price=None, max_price=None):
        """Scrape products from Flipkart"""
        products = []
        driver = self.create_driver()
        if not driver:
            return products
            
        try:
            # Build Flipkart search URL
            search_query = quote_plus(query)
            base_url = f"https://www.flipkart.com/search?q={search_query}"
            
            if min_price or max_price:
                base_url += f"&p%5B%5D=facets.price_range.from%3D{min_price or 0}&p%5B%5D=facets.price_range.to%3D{max_price or 100000}"
            
            logging.info(f"[FLIPKART] Scraping: {base_url}")
            driver.get(base_url)
            time.sleep(3)

            # Close popups
            try:
                close_btn = driver.find_element(By.XPATH, "//button[text()='✕']")
                close_btn.click()
                time.sleep(1)
            except:
                pass

            # Find products
            product_selectors = ["div[data-id]", "div._1AtVbE", "div._4ddWXP"]
            product_blocks = []
            
            for selector in product_selectors:
                product_blocks = driver.find_elements(By.CSS_SELECTOR, selector)
                if product_blocks:
                    break

            for block in product_blocks[:15]:  # Limit to 15 products
                try:
                    # Try multiple selectors for title
                    title = self.extract_text(block, [
                        "div._4rR01T", "a.IRpwTa", "div.KzDlHZ", 
                        "a._1fQZEK", "div._2WkVRV", "a.s1Q9rs"
                    ])
                    
                    # Try multiple selectors for price
                    price_text = self.extract_text(block, [
                        "div._30jeq3", "div._1_WHN1", "div.Nx9bqj", 
                        "div._25b18c", "span._1_WHN1"
                    ])
                    
                    # Try to get rating
                    rating = self.extract_text(block, [
                        "div._3LWZlK", "span._1lRcqv", "div._3Dp8La"
                    ])
                    
                    # Try to get image
                    image_url = self.extract_attribute(block, [
                        "img._396cs4", "img._2r_T1I", "img"
                    ], "src")

                    if title and price_text:
                        # Clean price
                        price = self.clean_price(price_text)
                        if price:
                            products.append({
                                "title": title,
                                "price": price,
                                "rating": rating or "No rating",
                                "source": "Flipkart",
                                "image_url": image_url,
                                "url": base_url
                            })
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            logging.error(f"Flipkart scraping error: {e}")
        finally:
            driver.quit()
            
        logging.info(f"[FLIPKART] Found {len(products)} products")
        return products

    def scrape_myntra(self, query, min_price=None, max_price=None):
        """Scrape products from Myntra"""
        products = []
        driver = self.create_driver()
        if not driver:
            return products
            
        try:
            search_query = quote_plus(query)
            base_url = f"https://www.myntra.com/{search_query}"
            
            logging.info(f"[MYNTRA] Scraping: {base_url}")
            driver.get(base_url)
            time.sleep(4)

            # Find products
            product_selectors = ["li.product-base", "div.product-base", ".product-productMetaInfo"]
            product_blocks = []
            
            for selector in product_selectors:
                product_blocks = driver.find_elements(By.CSS_SELECTOR, selector)
                if product_blocks:
                    break

            for block in product_blocks[:15]:
                try:
                    # Try multiple selectors for title
                    title = self.extract_text(block, [
                        "h3.product-brand", "h4.product-product", 
                        ".product-brand", ".product-product"
                    ])
                    
                    # Try multiple selectors for price
                    price_text = self.extract_text(block, [
                        ".product-discountedPrice", ".product-price",
                        "span.product-discountedPrice", "span.product-price"
                    ])
                    
                    # Try to get rating
                    rating = self.extract_text(block, [
                        ".product-ratingsContainer", ".product-rating"
                    ])
                    
                    # Try to get image
                    image_url = self.extract_attribute(block, [
                        "img.product-image", "img"
                    ], "src")

                    if title and price_text:
                        price = self.clean_price(price_text)
                        if price:
                            products.append({
                                "title": title,
                                "price": price,
                                "rating": rating or "No rating",
                                "source": "Myntra",
                                "image_url": image_url,
                                "url": base_url
                            })
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            logging.error(f"Myntra scraping error: {e}")
        finally:
            driver.quit()
            
        logging.info(f"[MYNTRA] Found {len(products)} products")
        return products

    def scrape_amazon(self, query, min_price=None, max_price=None):
        """Scrape products from Amazon"""
        products = []
        driver = self.create_driver()
        if not driver:
            return products
            
        try:
            search_query = quote_plus(query)
            base_url = f"https://www.amazon.in/s?k={search_query}"
            
            if min_price or max_price:
                base_url += f"&rh=p_36%3A{(min_price or 0)*100}-{(max_price or 100000)*100}"
            
            logging.info(f"[AMAZON] Scraping: {base_url}")
            driver.get(base_url)
            time.sleep(3)

            # Find products
            product_blocks = driver.find_elements(By.CSS_SELECTOR, "[data-component-type='s-search-result']")

            for block in product_blocks[:15]:
                try:
                    # Title
                    title = self.extract_text(block, [
                        "h2 a span", "h2 span", ".a-color-base.a-text-normal"
                    ])
                    
                    # Price
                    price_text = self.extract_text(block, [
                        ".a-price-whole", ".a-price .a-offscreen", ".a-price-symbol"
                    ])
                    
                    # Rating
                    rating = self.extract_text(block, [
                        ".a-icon-alt", ".a-rating .a-icon-alt"
                    ])
                    
                    # Image
                    image_url = self.extract_attribute(block, ["img"], "src")

                    if title and price_text:
                        price = self.clean_price(price_text)
                        if price:
                            products.append({
                                "title": title,
                                "price": price,
                                "rating": rating or "No rating",
                                "source": "Amazon",
                                "image_url": image_url,
                                "url": base_url
                            })
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            logging.error(f"Amazon scraping error: {e}")
        finally:
            driver.quit()
            
        logging.info(f"[AMAZON] Found {len(products)} products")
        return products

    def extract_text(self, element, selectors):
        """Extract text using multiple selector fallbacks"""
        for selector in selectors:
            try:
                elem = element.find_element(By.CSS_SELECTOR, selector)
                text = elem.text.strip()
                if text:
                    return text
            except:
                continue
        return None

    def extract_attribute(self, element, selectors, attribute):
        """Extract attribute using multiple selector fallbacks"""
        for selector in selectors:
            try:
                elem = element.find_element(By.CSS_SELECTOR, selector)
                attr = elem.get_attribute(attribute)
                if attr:
                    return attr
            except:
                continue
        return None

    def clean_price(self, price_text):
        """Clean and extract numeric price from price text"""
        try:
            # Remove currency symbols and extract numbers
            price_clean = re.sub(r'[^\d,]', '', price_text)
            price_clean = price_clean.replace(',', '')
            if price_clean and price_clean.isdigit():
                return int(price_clean)
        except:
            pass
        return None

    def search_all_stores(self, query, min_price=None, max_price=None):
        """Search products from all stores concurrently"""
        all_products = []
        
        # Use ThreadPoolExecutor for concurrent scraping
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit scraping tasks
            future_flipkart = executor.submit(self.scrape_flipkart, query, min_price, max_price)
            future_myntra = executor.submit(self.scrape_myntra, query, min_price, max_price)
            future_amazon = executor.submit(self.scrape_amazon, query, min_price, max_price)
            
            # Collect results
            try:
                flipkart_products = future_flipkart.result(timeout=30)
                all_products.extend(flipkart_products)
            except Exception as e:
                logging.error(f"Flipkart scraping failed: {e}")
                
            try:
                myntra_products = future_myntra.result(timeout=30)
                all_products.extend(myntra_products)
            except Exception as e:
                logging.error(f"Myntra scraping failed: {e}")
                
            try:
                amazon_products = future_amazon.result(timeout=30)
                all_products.extend(amazon_products)
            except Exception as e:
                logging.error(f"Amazon scraping failed: {e}")

        # Sort by price (lowest first)
        all_products.sort(key=lambda x: x.get('price', float('inf')))
        
        # Add position for voice feedback
        for i, product in enumerate(all_products):
            product['position'] = i + 1
            
        logging.info(f"[TOTAL] Found {len(all_products)} products across all stores")
        return all_products
