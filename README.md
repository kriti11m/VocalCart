# VocalCart - Real-time Voice Shopping Assistant

🛍️ **Real-time product scraping with voice-controlled UI and modern web interface**

## 🚀 New Architecture (v3.0)

VocalCart now features a **modern, voice-accessible frontend** with a **real-time, no-database backend architecture** that scrapes live e-commerce data and provides instant results through voice commands.

### 🏗️ Technical Stack

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Modern Frontend │───▶│   FastAPI API    │───▶│  Live Scrapers  │
│ (HTML/CSS/JS)   │    │  (No Database)   │    │ (Flipkart/      │
│ Voice-enabled   │    │                  │    │  Amazon)        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                        │                       │
         │                        ▼                       │
┌─────────────────┐    ┌──────────────────┐              │
│  Web Speech API │◀───│  JSON Response   │◀─────────────┘
│ (Voice I/O)     │    │  (In Memory)     │
└─────────────────┘    └──────────────────┘
```

### 🎯 Key Features

- **🌍 Real-time Data**: Live scraping from Flipkart, Amazon
- **🎤 Voice Interface**: Web Speech API for recognition and synthesis
- **🖥️ Modern UI**: Responsive design with accessibility features
- **⚡ No Database**: All data in-memory, always fresh
- **🔄 Session Management**: In-memory state tracking
- **📡 RESTful API**: FastAPI with async scraping
- **🎭 Multi-store**: Concurrent scraping across platforms
- **♿ Enhanced Accessibility**: 
  - Auto-starting tutorial for blind users
  - Interactive voice-over guidance
  - Screen reader optimization
  - ARIA live regions
  - Keyboard shortcuts for all actions
  - Skip links for keyboard navigation
- **🔍 Product Display**: Real-time image and data visualization

## 📁 Project Structure

```
VocalCart/
├── main.py                    # Entry point
├── fastapi_server.py          # FastAPI app with session management
├── routers/
│   ├── search.py             # Product search endpoints
│   ├── navigate.py           # Navigation commands (next/prev/buy)
│   ├── cart.py               # Shopping cart operations
│   └── tts.py                # Text-to-speech endpoints
├── services/
│   ├── parser.py             # Query parsing & NLP
│   ├── scraper_flipkart.py   # Flipkart scraper
│   ├── scraper_amazon.py     # Amazon scraper
│   └── multi_store_scraper.py # Multi-store coordinator
├── utils/
│   └── voice.py              # Voice input/output utilities
├── templates/
│   └── index.html            # Main web interface
├── static/
│   ├── css/
│   │   ├── styles.css        # Application styles
│   │   ├── accessibility.css # Accessibility style enhancements
│   │   └── fix-frontend.css  # Frontend restoration styles
│   ├── js/
│   │   ├── app.js            # Frontend JavaScript
│   │   ├── accessibility-tutorial.js # Step-by-step tutorial
│   │   ├── audio-tutorial.js # Audio guide for blind users
│   │   └── auto-start-tutorial.js    # Auto-start tutorial logic
│   └── favicon.ico           # Site favicon
├── requirements.txt          # Dependencies
└── demo_realtime_api.py      # API testing script
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Chrome or Chromium browser (for WebDriver)
- Required OS packages:
  ```bash
  # For Ubuntu/Debian:
  apt-get install -y python3-dev build-essential libssl-dev

  # For macOS:
  brew install openssl
  ```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Required Directories

```bash
# Create directory for cart storage
mkdir -p carts
```

### 4. Check WebDriver Compatibility

VocalCart provides a compatibility checker for Selenium WebDriver. This is particularly useful if you encounter connection errors:

```bash
# Run the WebDriver compatibility checker
python check_webdriver.py
```

The checker will tell you if your environment supports Selenium-based scraping or if you should use simple mode.

### 5. Start the Server

#### Standard Mode (with Selenium WebDriver)
```bash
python run.py
```

#### Simple Mode (No Selenium - for environments with compatibility issues)
If you encounter WebDriver connection errors or the compatibility checker recommends simple mode:

```bash
python run.py --simple-mode
```

The application will start on `http://localhost:5004` by default.

### 6. Access the Web Interface

Open your browser and go to:
```
http://localhost:5004
```

### 4. Test API Directly (Optional)

```bash
# Run the demo script
python demo_realtime_api.py

# Or interactive mode
python demo_realtime_api.py interactive
```

## 📡 API Endpoints

### 🔍 Search Products

```bash
curl -X POST http://localhost:5002/api/voice-command \
  -H "Content-Type: application/json" \
  -d '{"command": "find shoes under 2000 rupees"}'
```

### ➡️ Navigate Results

```bash
curl -X POST http://localhost:5002/api/navigate \
  -H "Content-Type: application/json" \
  -d '{"command": "next", "session_id": "default"}'
```

### � Shopping Cart

```bash
# Add to cart
curl -X POST http://localhost:5002/api/cart/add \
  -H "Content-Type: application/json" \
  -d '{"product": {"title": "Test Product", "price": 1999}, "session_id": "default"}'

# View cart
curl -X GET http://localhost:5002/api/cart/items?session_id=default

# Remove from cart
curl -X POST http://localhost:5002/api/cart/remove \
  -H "Content-Type: application/json" \
  -d '{"item_title": "Test Product", "session_id": "default"}'

# Checkout
curl -X POST http://localhost:5002/api/cart/checkout \
  -H "Content-Type: application/json" \
  -d '{"session_id": "default"}'
```

### �🔊 Text-to-Speech

```bash
curl -X POST http://localhost:5002/api/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Welcome to VocalCart!"}' \
  --output speech.mp3
```

## 🎤 Voice Commands

### Search Commands
- "Find shoes under 2000"
- "Search for wireless earphones"
- "Show me smartphones under 20000"
- "Get laptops between 30000 and 50000"

### Navigation Commands
- "Next" - Move to next product
- "Previous" - Go to previous product
- "Repeat" - Repeat current product
- "First" - Go to first product
- "Last" - Go to last product
- "Buy this" - Get purchase link

### Action Commands
- "Buy this" - Open product page
- "Add item 3 to cart" - Add specific product to cart
- "Tell me about item 2" - Get product details
- "Show my cart" - Review current shopping cart
- "Checkout" - Proceed to checkout
- "Clear cart" - Remove all items from cart

## 🛠️ Configuration

### Configuration File (config.json)

VocalCart now uses a configuration file for better customization. A default file is automatically created if it doesn't exist:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5004,
    "reload": true
  },
  "scraping": {
    "default_timeout": 30,
    "use_headless": true,
    "disable_selenium": false,
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
```

### Environment Variables

```bash
export VOCALCART_HOST=0.0.0.0          # Server host
export VOCALCART_PORT=5004             # Server port
export VOCALCART_DISABLE_SELENIUM=0    # Set to 1 to disable Selenium
```

### Running Options

```bash
# Run with default settings
python run.py

# Run with simple mode (no Selenium)
python run.py --simple-mode

# Specify a custom port
python run.py --port 8000

# Specify a custom server file
python run.py --file main.py

# Run directly (without subprocess)
python run.py --direct
```

### Scraper Settings

The scrapers are optimized for speed with multiple modes:

#### Full Mode (Selenium-based)
- Headless Chrome browser
- Concurrent multi-store scraping
- Intelligent fallback data
- Timeout protection

#### Simple Mode (No Selenium)
- Pure requests/BeautifulSoup scraping
- No browser dependency
- Lower resource usage
- Works in environments where WebDriver fails

## 🔧 Development

### Running in Development Mode

```bash
# With auto-reload
python main.py

# Or using uvicorn directly
uvicorn fastapi_server:app --reload --port 5002
```

### Testing Individual Components

```python
# Test parser
from services.parser import QueryParser
parser = QueryParser()
result = parser.parse_search_query("shoes under 2000")

# Test scraper
from services.scraper_flipkart import FlipkartScraper
scraper = FlipkartScraper()
products = scraper.search("shoes", max_price=2000)
```

## 📊 Session Management

Sessions are stored in-memory with the following structure:

```python
{
  "session_id": {
    "current_products": [],     # Latest search results
    "current_index": 0,         # Current product index
    "last_query": "",          # Last search query
    "session_active": True     # Session status
  }
}
```

## 🎯 Real-time Flow

1. **User Voice Command** → Speech-to-Text
2. **Query Parsing** → Extract keywords, price, category
3. **Live Scraping** → Fetch from Flipkart/Amazon concurrently
4. **JSON Response** → Format results for voice
5. **Text-to-Speech** → Announce first product
6. **Navigation** → Handle next/previous/buy commands
7. **Cart Operations** → Add/remove items, checkout
8. **Session Management** → Track user cart across visits

## 🌟 Advantages of This Architecture

✅ **Always Fresh Data** - No stale database entries  
✅ **Faster Development** - No database setup/maintenance  
✅ **Scalable** - Add caching layer when needed  
✅ **Real-time** - Live product availability & pricing  
✅ **Flexible** - Easy to add new stores  

## 🚦 Performance

- **Search Response**: 3-8 seconds (live scraping)
- **Navigation**: <100ms (in-memory)
- **Concurrent Stores**: 2-3 stores simultaneously
- **Session Storage**: RAM only, no persistence

## ♿ Accessibility Features

### Auto-Starting Tutorial for Blind Users
- Automatically detects screen readers and starts a comprehensive audio tutorial
- Modal dialog with keyboard focus trap for tutorial content
- ARIA live regions announce important information
- Step-by-step guidance on using all application features

### Interactive Voice-Over Tutorial
- Detailed audio explanations of all UI elements and functions
- Keyboard shortcut guidance for blind users
- Voice-driven navigation and product search instructions
- Cart management and checkout process explanation

### Keyboard Navigation
- **Ctrl+Space**: Start/stop tutorial
- **Alt+T**: Toggle tutorial
- **Spacebar**: Pause/resume tutorial
- **Escape**: Close tutorial modal
- **Tab**: Navigate through interactive elements
- **Enter**: Select current item

### Screen Reader Optimizations
- ARIA labels and landmarks throughout the application
- Skip links for bypassing repetitive content
- Focus management for modal dialogs
- Semantic HTML structure for better navigation
- Status announcements for search results and actions

### Accessibility Components
- `accessibility-tutorial.js`: Step-by-step interactive tutorial
- `audio-tutorial.js`: Comprehensive audio guide with blind-specific instructions
- `auto-start-tutorial.js`: Ensures tutorial auto-starts for screen reader users
- `fix-frontend.css`: Enhanced styling for accessibility

## 🔮 Future Enhancements

- **Redis Caching** for production scaling
- **WebSocket** real-time updates
- **More Stores** (Myntra, Meesho, etc.)
- **Voice Recognition** improvements
- **Product Comparison** features
- **Price Alerts** and notifications
- **User Accounts** with persistent carts
- **Payment Integration** for complete checkout
- **Order History** and tracking
- **Personalized Recommendations** based on cart history

## ⚠️ Troubleshooting

### Selenium Connection Errors

If you see errors like this:

```
WARNING:urllib3.connectionpool:Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x...>: Failed to establish a new connection: [Errno 61] Connection refused')': /session/...
```

This indicates the WebDriver cannot establish a connection with Chrome. Solutions:

1. **Run in Simple Mode**:
   ```bash
   python run.py --simple-mode
   ```

2. **Check Chrome Installation**:
   - Ensure Chrome or Chromium is installed
   - Check that it's in the standard location for your OS

3. **Install WebDriver Manually**:
   ```bash
   # Download ChromeDriver that matches your Chrome version
   # Add it to your PATH
   ```

4. **Check Firewall/Antivirus**: Some security software blocks WebDriver

5. **Run the WebDriver Checker**:
   ```bash
   python check_webdriver.py
   ```

### Port Already in Use

If you see "Address already in use" errors:
```bash
# Use a different port
python run.py --port 8080
```

## 📝 Example Usage

```python
import requests

# Search for products
response = requests.post("http://localhost:5002/api/voice-command", 
    json={"command": "find wireless earphones under 1500"})

result = response.json()
print(f"Found {len(result['products'])} products")

# Navigate through results
requests.post("http://localhost:5002/api/navigate", 
    json={"command": "next", "session_id": "default"})
```

---

**🎤 "Hey VocalCart, find me the best deals!" 🛍️**
