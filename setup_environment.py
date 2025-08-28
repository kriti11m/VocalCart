#!/usr/bin/env python3
"""
Setup environment for VocalCart - ensures all required dependencies are installed
and Chrome/ChromeDriver are properly configured for real-time scraping
"""

import os
import sys
import subprocess
import logging
import platform

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_install_dependencies():
    """Check and install required dependencies"""
    logger.info("Checking and installing required dependencies...")
    
    requirements = [
        "selenium",
        "webdriver-manager",
        "beautifulsoup4",
        "requests",
        "fastapi",
        "uvicorn",
        "pydantic",
        "aiohttp",
        "lxml"
    ]
    
    try:
        # Check if pip is available
        subprocess.check_call([sys.executable, "-m", "pip", "--version"])
        
        # Install required packages
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade"
        ] + requirements)
        
        logger.info("Successfully installed Python dependencies")
        return True
    except Exception as e:
        logger.error(f"Error installing dependencies: {e}")
        return False

def setup_chrome_driver():
    """Set up ChromeDriver for real-time scraping"""
    logger.info("Setting up ChromeDriver...")
    
    try:
        # First, ensure selenium and webdriver-manager are installed
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade",
            "selenium", "webdriver-manager"
        ])
        
        # Now try to download and set up ChromeDriver
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        
        # Download and install ChromeDriver
        driver_path = ChromeDriverManager().install()
        
        # Make the driver executable
        os.chmod(driver_path, 0o755)
        
        logger.info(f"ChromeDriver installed at: {driver_path}")
        
        # Test the driver with minimal options
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument("--headless")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        # Try to visit a simple page
        driver.get("https://www.google.com")
        driver.quit()
        
        logger.info("ChromeDriver setup and tested successfully")
        return True
    except Exception as e:
        logger.error(f"Error setting up ChromeDriver: {e}")
        logger.info("You may need to install Chrome browser manually")
        return False

def check_system_compatibility():
    """Check if the system is compatible for real-time scraping"""
    system = platform.system()
    logger.info(f"Detecting system: {system}")
    
    if system == "Darwin":  # macOS
        # Check Chrome installation
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium"
        ]
        
        chrome_installed = any(os.path.exists(path) for path in chrome_paths)
        
        if not chrome_installed:
            logger.warning("Chrome is not installed at the standard location.")
            logger.info("Please install Chrome from https://www.google.com/chrome/")
    
    elif system == "Linux":
        # Check Chrome on Linux
        try:
            result = subprocess.run(["which", "google-chrome"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning("Chrome is not installed or not in PATH")
                logger.info("Install Chrome with: sudo apt install google-chrome-stable")
        except:
            logger.warning("Could not detect Chrome installation")
    
    elif system == "Windows":
        # Check Chrome on Windows
        chrome_path = os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), 
                                  "Google\\Chrome\\Application\\chrome.exe")
        chrome_path_x86 = os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), 
                                      "Google\\Chrome\\Application\\chrome.exe")
        
        if not (os.path.exists(chrome_path) or os.path.exists(chrome_path_x86)):
            logger.warning("Chrome is not installed at the standard location.")
            logger.info("Please install Chrome from https://www.google.com/chrome/")

def main():
    """Main setup function"""
    logger.info("Setting up VocalCart environment for real-time scraping")
    
    # Check system compatibility
    check_system_compatibility()
    
    # Install dependencies
    if not check_and_install_dependencies():
        logger.error("Failed to install required dependencies")
        return False
    
    # Set up ChromeDriver
    if not setup_chrome_driver():
        logger.error("Failed to set up ChromeDriver")
        logger.info("VocalCart may not be able to scrape real-time data")
        return False
    
    logger.info("VocalCart environment setup complete!")
    logger.info("You can now use real-time product scraping")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
