from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def search_flipkart(query, min_price=None, max_price=None):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    try:
        # Build search URL
        base_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        if min_price or max_price:
            base_url += f"&p%5B%5D=facets.price_range.from%3D{min_price or 0}&p%5B%5D=facets.price_range.to%3D{max_price or 100000}"
        print("[DEBUG] URL:", base_url)

        driver.get(base_url)
        time.sleep(4)

        # Close login popup if present
        try:
            close_btn = driver.find_element(By.XPATH, "//button[text()='✕']")
            close_btn.click()
        except:
            pass

        # Scroll to load more content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Find product blocks (updated to be more robust)
        product_blocks = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")
        print("[DEBUG] Found product blocks:", len(product_blocks))

        results = []

        for block in product_blocks:
            try:
                title = block.find_element(By.CSS_SELECTOR, "div._4rR01T, a.IRpwTa").text
                price = block.find_element(By.CSS_SELECTOR, "div._30jeq3").text
                price = int(price.replace("₹", "").replace(",", ""))
                results.append({
                    "title": title,
                    "price": price
                })
            except Exception as e:
                continue

        print(f"[DEBUG] Extracted {len(results)} products")
        return results

    finally:
        driver.quit()
