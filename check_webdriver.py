#!/usr/bin/env python3
"""
WebDriver Compatibility Check

This script checks if Selenium WebDriver can run properly in the current environment
and provides guidance for using VocalCart with or without Selenium.
"""

import os
import sys
import platform
import logging
import subprocess
import tempfile
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("webdriver-check")

def check_selenium_imports():
    """Check if Selenium and related packages are properly installed"""
    try:
        import selenium
        logger.info(f"Selenium installed: {selenium.__version__}")
        
        from selenium import webdriver
        logger.info("Selenium WebDriver module is available")
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            logger.info("WebDriver Manager is available")
        except ImportError:
            logger.warning("WebDriver Manager not installed - using system ChromeDriver only")
            
        return True
    except ImportError as e:
        logger.error(f"Selenium import error: {e}")
        return False

def check_browser_availability():
    """Check if Chrome/Chromium is available"""
    browser_paths = []
    
    if platform.system() == "Darwin":  # macOS
        browser_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium"
        ]
    elif platform.system() == "Windows":
        browser_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Chromium\Application\chrome.exe"
        ]
    else:  # Linux
        browser_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
    
    for path in browser_paths:
        if os.path.exists(path):
            logger.info(f"Browser found: {path}")
            return True
            
    logger.error("No compatible browser found")
    return False

def test_selenium_operation():
    """Test if Selenium WebDriver works properly"""
    
    # Create a small test script
    test_script = """
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

try:
    # Configure options
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Try with ChromeDriverManager if available
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except:
        # Try with default Chrome
        driver = webdriver.Chrome(options=options)
    
    # Test navigation
    driver.get("https://www.google.com")
    print(f"Page title: {driver.title}")
    
    # Close browser
    driver.quit()
    print("SUCCESS: Selenium test completed successfully")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
"""

    # Write test script to temp file
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
        f.write(test_script)
        test_file = f.name
    
    try:
        # Execute test script
        logger.info("Testing Selenium WebDriver...")
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and "SUCCESS" in result.stdout:
            logger.info("Selenium WebDriver test successful!")
            return True
        else:
            logger.error(f"Selenium WebDriver test failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error("Selenium WebDriver test timed out")
        return False
    finally:
        # Clean up temp file
        try:
            os.unlink(test_file)
        except:
            pass

def main():
    """Main function to check WebDriver compatibility"""
    print("\n" + "="*60)
    print("VocalCart WebDriver Compatibility Check")
    print("="*60)
    
    print("\nChecking environment...")
    
    # Check Python version
    py_version = platform.python_version()
    print(f"Python version: {py_version}")
    if tuple(map(int, py_version.split('.')[:2])) < (3, 7):
        print("❌ Python 3.7+ is required")
    else:
        print("✅ Python version OK")
    
    # Check OS
    system = platform.system()
    print(f"Operating system: {system} {platform.version()}")
    
    # Check imports
    print("\nChecking Selenium installation...")
    imports_ok = check_selenium_imports()
    
    # Check browser
    print("\nChecking browser availability...")
    browser_ok = check_browser_availability()
    
    # Test Selenium operation if prerequisites are met
    selenium_works = False
    if imports_ok and browser_ok:
        print("\nTesting Selenium WebDriver operation...")
        selenium_works = test_selenium_operation()
    
    # Display results and recommendations
    print("\n" + "="*60)
    print("COMPATIBILITY RESULTS")
    print("="*60)
    
    if selenium_works:
        print("\n✅ SELENIUM FULLY COMPATIBLE")
        print("\nRecommendation:")
        print("  Run VocalCart normally with real-time scraping:")
        print(f"  {sys.executable} run.py")
    else:
        print("\n❌ SELENIUM COMPATIBILITY ISSUES DETECTED")
        print("\nRecommendation:")
        print("  Run VocalCart in SIMPLE MODE without Selenium:")
        print(f"  {sys.executable} run.py --simple-mode")
        
        if not imports_ok:
            print("\nTo fix Selenium imports:")
            print("  pip install selenium webdriver-manager")
        
        if not browser_ok:
            print("\nTo fix browser availability:")
            print("  Install Google Chrome or Chromium")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
