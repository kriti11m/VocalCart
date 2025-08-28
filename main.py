#!/usr/bin/env python3
"""
VocalCart - Real-time Voice-powered Shopping Assistant
Main entry point for the FastAPI server

No database dependency - uses real-time scraping with in-memory session management
"""

import os
import sys
import uvicorn
import logging

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    try:
        # Import the FastAPI app
        from fastapi_server import app
        
        # Configuration
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", 5002))
        reload = os.getenv("RELOAD", "true").lower() == "true"
        
        logger.info(f"Starting VocalCart API server on {host}:{port}")
        logger.info("Features: Real-time scraping, Voice commands, No database")
        
        # Run the server
        uvicorn.run(
            "fastapi_server:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Please install required dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
