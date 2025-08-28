#!/usr/bin/env python3
"""
VocalCart Runner Script
Helper script to run VocalCart with proper error handling and configuration
"""

import os
import sys
import json
import argparse
import logging
import platform
import subprocess
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("vocalcart-runner")

def load_config():
    """Load configuration from config.json or create default"""
    config_file = Path("config.json")
    if not config_file.exists():
        logger.info("Creating default configuration file")
        default_config = {
            "server": {
                "host": "0.0.0.0",
                "port": 5004,
                "reload": True
            },
            "scraping": {
                "default_timeout": 30,
                "use_headless": True,
                "disable_selenium": False,  # Add option to disable Selenium
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
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        return default_config
    
    try:
        with open(config_file, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        logger.info("Using default configuration")
        return {
            "server": {"host": "0.0.0.0", "port": 5004, "reload": True},
            "scraping": {"default_timeout": 30, "use_headless": True, "disable_selenium": False},
            "session": {"cart_dir": "carts"}
        }

def ensure_directories():
    """Create necessary directories if they don't exist"""
    directories = ["carts", "static/css", "static/js"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def check_python_version():
    """Verify Python version compatibility"""
    if sys.version_info < (3, 7):
        logger.error(f"Python 3.7+ required. Found: {platform.python_version()}")
        return False
    return True

def patch_selenium_environment():
    """Apply environment patches for Selenium WebDriver"""
    # Set environment variables that might help with Selenium issues
    os.environ["WDM_LOG_LEVEL"] = "0"  # Reduce WebDriver Manager logging
    os.environ["WDM_PRINT_FIRST_LINE"] = "False"  # Disable WebDriver Manager welcome
    
    # For macOS, ensure proper PATH for Chrome
    if platform.system() == "Darwin":
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS",
            "/Applications/Chromium.app/Contents/MacOS"
        ]
        for path in chrome_paths:
            if os.path.exists(path) and path not in os.environ.get("PATH", ""):
                os.environ["PATH"] = f"{path}:{os.environ.get('PATH', '')}"
    
    # Disable GPU and sandbox for headless Chrome
    os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning"
    
    # Set specific options for Chrome
    os.environ["SELENIUM_CHROME_ARGS"] = "--no-sandbox,--disable-dev-shm-usage,--disable-gpu"

def disable_selenium_in_config():
    """Modify config to disable Selenium-based scraping"""
    config_file = Path("config.json")
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            
            if "scraping" not in config:
                config["scraping"] = {}
            
            config["scraping"]["disable_selenium"] = True
            
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
                
            logger.info("Updated config to disable Selenium-based scraping")
        except Exception as e:
            logger.error(f"Failed to update config: {e}")

def run_server(config, args):
    """Run the FastAPI server"""
    try:
        # Set environment variables
        os.environ["VOCALCART_DISABLE_SELENIUM"] = "1" if args.disable_selenium else "0"
        os.environ["VOCALCART_HOST"] = config["server"]["host"]
        os.environ["VOCALCART_PORT"] = str(config["server"]["port"])
        
        # If --simple-mode specified, disable Selenium in config
        if args.simple_mode:
            disable_selenium_in_config()
            os.environ["VOCALCART_DISABLE_SELENIUM"] = "1"
        
        # Determine server file to use
        server_file = args.file if args.file else "fastapi_server.py"
        if not os.path.exists(server_file):
            server_file = "main.py"
            if not os.path.exists(server_file):
                logger.error("Could not find server file (fastapi_server.py or main.py)")
                return False
        
        # Build command
        host = config["server"]["host"]
        port = config["server"]["port"]
        
        # Direct startup
        if args.direct:
            import uvicorn
            logger.info(f"Starting server directly on {host}:{port}")
            
            # Get the app object dynamically
            module_name = server_file[:-3] if server_file.endswith('.py') else server_file
            sys.path.insert(0, os.path.dirname(os.path.abspath(server_file)))
            module = __import__(module_name)
            app = getattr(module, "app")
            
            # Start with uvicorn
            uvicorn.run(
                app,
                host=host,
                port=port,
                reload=config["server"].get("reload", True)
            )
            return True
        
        # Use subprocess - more reliable generally
        cmd = [sys.executable, server_file]
        
        logger.info(f"Starting server using: {' '.join(cmd)}")
        logger.info(f"Server will be available at http://{host}:{port}")
        
        if args.simple_mode:
            logger.info("Running in SIMPLE MODE - Selenium disabled for compatibility")
        
        print("\n" + "="*70)
        print(f" VocalCart is starting at http://{host}:{port}")
        print("="*70)
        print(" Press Ctrl+C to stop the server")
        print(f" Frontend will be available at http://{host}:{port}")
        print(" Voice commands ready for use!")
        print("="*70 + "\n")
        
        # Run the server process
        process = subprocess.Popen(
            cmd,
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream the output
        for line in process.stdout:
            print(line.strip())
            if "Uvicorn running on" in line or "Application startup complete" in line:
                logger.info("Server started successfully!")
        
        return True
    
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        return True
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        return False

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="VocalCart Runner")
    parser.add_argument("--port", type=int, help="Port to run the server on")
    parser.add_argument("--file", help="Server file to run (default: fastapi_server.py)")
    parser.add_argument("--simple-mode", action="store_true", help="Run in simple mode (disables Selenium)")
    parser.add_argument("--disable-selenium", action="store_true", help="Disable Selenium WebDriver")
    parser.add_argument("--direct", action="store_true", help="Start server directly without subprocess")
    return parser.parse_args()

def main():
    """Main entry point"""
    print("\nStarting VocalCart Runner...")
    
    # Parse arguments
    args = parse_args()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create required directories
    ensure_directories()
    
    # Load configuration
    config = load_config()
    
    # Apply port override if specified
    if args.port:
        config["server"]["port"] = args.port
    
    # Patch environment for Selenium
    patch_selenium_environment()
    
    # Run the server
    success = run_server(config, args)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
