#!/usr/bin/env python3

"""
VocalCart Installation Script
Helps set up all dependencies and verify the environment for VocalCart.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def print_header(message):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f" {message}")
    print("="*70)

def print_step(message):
    """Print a step message"""
    print(f"\n▶ {message}")

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print a warning message"""
    print(f"⚠️ {message}")

def run_command(command, description=None, exit_on_error=False):
    """Run a shell command and return the result"""
    if description:
        print_step(description)
    
    print(f"   Running: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True, 
                               check=False)
        
        if result.returncode == 0:
            if result.stdout:
                print(f"   Output: {result.stdout[:100].strip()}{'...' if len(result.stdout) > 100 else ''}")
            print_success("Command completed successfully")
            return True, result.stdout
        else:
            print_error(f"Command failed with code {result.returncode}")
            print(f"   Error: {result.stderr.strip()}")
            if exit_on_error:
                print_error("Exiting installation due to error")
                sys.exit(1)
            return False, result.stderr
    except Exception as e:
        print_error(f"Failed to run command: {e}")
        if exit_on_error:
            sys.exit(1)
        return False, str(e)

def check_python_version():
    """Check if Python version is compatible"""
    print_step("Checking Python version")
    
    if sys.version_info < (3, 8):
        print_error(f"Python 3.8 or higher is required. Found {platform.python_version()}")
        print_warning("Please upgrade your Python version and try again")
        return False
    
    print_success(f"Python version {platform.python_version()} is compatible")
    return True

def create_directories():
    """Create necessary directories"""
    print_step("Creating necessary directories")
    
    directories = [
        "carts",
        "static/css",
        "static/js"
    ]
    
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"   Created directory: {directory}")
            except Exception as e:
                print_error(f"Failed to create directory {directory}: {e}")
                return False
        else:
            print(f"   Directory already exists: {directory}")
    
    print_success("All directories created successfully")
    return True

def install_requirements():
    """Install Python requirements"""
    print_step("Installing Python dependencies")
    
    requirements_file = "requirements.txt"
    
    if not os.path.exists(requirements_file):
        print_error(f"Requirements file {requirements_file} not found")
        return False
    
    success, _ = run_command(
        [sys.executable, "-m", "pip", "install", "-r", requirements_file],
        description="Installing Python packages from requirements.txt"
    )
    
    return success

def check_chrome():
    """Check if Chrome or Chromium is installed"""
    print_step("Checking for Chrome/Chromium browser")
    
    system = platform.system()
    
    if system == "Linux":
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                print_success(f"Found Chrome/Chromium at: {path}")
                return True
        
        print_warning("Chrome/Chromium not found in standard locations")
        print("Please install Chrome or Chromium browser:")
        print("   sudo apt-get install -y chromium-browser")
        return False
    
    elif system == "Darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium"
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                print_success(f"Found Chrome/Chromium at: {path}")
                return True
        
        print_warning("Chrome/Chromium not found in standard locations")
        print("Please install Chrome browser from https://www.google.com/chrome/")
        return False
    
    elif system == "Windows":
        chrome_paths = [
            os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Google\\Chrome\\Application\\chrome.exe'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Google\\Chrome\\Application\\chrome.exe')
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                print_success(f"Found Chrome at: {path}")
                return True
        
        print_warning("Chrome not found in standard locations")
        print("Please install Chrome browser from https://www.google.com/chrome/")
        return False
    
    else:
        print_warning(f"Unsupported operating system: {system}")
        print("Please install Chrome or Chromium browser manually")
        return False

def check_webdriver():
    """Check if webdriver is working"""
    print_step("Testing WebDriver functionality")
    
    try:
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        print("   Setting up ChromeDriverManager...")
        service = Service(ChromeDriverManager().install())
        
        print("   Creating WebDriver instance...")
        driver = webdriver.Chrome(service=service, options=options)
        
        print("   Testing WebDriver with simple page load...")
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print_success(f"WebDriver is working correctly! Loaded page with title: {title}")
        return True
    except Exception as e:
        print_error(f"WebDriver test failed: {e}")
        print_warning("You might need to install additional dependencies or configure your environment")
        return False

def check_fastapi():
    """Test if FastAPI is working"""
    print_step("Testing FastAPI functionality")
    
    try:
        import uvicorn
        from fastapi import FastAPI
        
        print_success("FastAPI imports are working correctly")
        return True
    except Exception as e:
        print_error(f"FastAPI test failed: {e}")
        return False

def setup_config():
    """Create a default config file if it doesn't exist"""
    print_step("Setting up configuration")
    
    config_file = "config.json"
    
    if not os.path.exists(config_file):
        default_config = {
            "server": {
                "host": "0.0.0.0",
                "port": 5004,
                "reload": True
            },
            "scraping": {
                "default_timeout": 30,
                "use_headless": True,
                "stores": ["flipkart", "amazon"]
            },
            "voice": {
                "language": "en-IN",
                "rate": 1.0,
                "pitch": 1.0
            },
            "session": {
                "cart_dir": "carts",
                "default_session_id": "default"
            }
        }
        
        try:
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            print_success(f"Created default configuration in {config_file}")
        except Exception as e:
            print_error(f"Failed to create configuration file: {e}")
            return False
    else:
        print(f"   Configuration file {config_file} already exists")
    
    return True

def main():
    """Main installation function"""
    print_header("VocalCart Installation and Setup")
    
    print("This script will check your environment and install required dependencies.")
    print("Make sure you have proper permissions to install Python packages.")
    
    # Check environment
    if not check_python_version():
        return
    
    # Create necessary directories
    create_directories()
    
    # Install Python dependencies
    install_requirements()
    
    # Check if Chrome is installed
    check_chrome()
    
    # Test WebDriver
    check_webdriver()
    
    # Check FastAPI
    check_fastapi()
    
    # Setup configuration
    setup_config()
    
    # Final message
    print_header("Installation Complete!")
    print("\nTo start VocalCart, run:")
    print("\n   python fastapi_server.py\n")
    print("Then open your browser at: http://localhost:5004")
    print("\nFor more information, see the README.md file.")

if __name__ == "__main__":
    main()
