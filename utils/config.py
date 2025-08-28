"""
VocalCart Config Module
Handles configuration loading and environment variables
"""

import os
import json
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json or create default"""
    config_file = Path("config.json")
    
    # Check environment variables first
    disable_selenium = os.environ.get("VOCALCART_DISABLE_SELENIUM", "0").lower() in ["1", "true", "yes"]
    host = os.environ.get("VOCALCART_HOST", "0.0.0.0")
    port = int(os.environ.get("VOCALCART_PORT", "5002"))
    
    # If config file exists, load it
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
                
            # Environment variables override config file
            if "VOCALCART_DISABLE_SELENIUM" in os.environ:
                if "scraping" not in config:
                    config["scraping"] = {}
                config["scraping"]["disable_selenium"] = disable_selenium
                
            if "VOCALCART_HOST" in os.environ:
                if "server" not in config:
                    config["server"] = {}
                config["server"]["host"] = host
                
            if "VOCALCART_PORT" in os.environ:
                if "server" not in config:
                    config["server"] = {}
                config["server"]["port"] = port
                
            return config
                
        except Exception as e:
            logger.warning(f"Error loading config file: {e}")
            # Fall back to default config
    
    # Create default config
    default_config = {
        "server": {
            "host": host,
            "port": port,
            "reload": True
        },
        "scraping": {
            "default_timeout": 30,
            "use_headless": True,
            "disable_selenium": disable_selenium,
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
    
    # Write default config if it doesn't exist
    try:
        if not config_file.exists():
            with open(config_file, "w") as f:
                json.dump(default_config, f, indent=2)
            logger.info("Created default configuration file")
    except Exception as e:
        logger.warning(f"Failed to write default config: {e}")
    
    return default_config

# Global configuration
config = load_config()

def get_config():
    """Get the current configuration"""
    return config

def is_selenium_disabled():
    """Check if Selenium is disabled"""
    return config.get("scraping", {}).get("disable_selenium", False)
