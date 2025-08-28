import re
import random
from typing import List, Dict, Any

class AccessibleProductDescriber:
    """
    Enhanced product description system designed specifically for blind users
    Provides detailed, voice-friendly product descriptions with accessibility features
    """
    
    def __init__(self):
        self.price_ranges = {
            'budget': (0, 1000),
            'affordable': (1000, 5000),
            'mid-range': (5000, 20000),
            'premium': (20000, 50000),
            'luxury': (50000, float('inf'))
        }
        
    def describe_product_for_accessibility(self, product: Dict[str, Any], position: int = None) -> str:
        """
        Generate comprehensive voice-friendly product description for blind users
        """
        description_parts = []
        
        # Position announcement
        if position:
            description_parts.append(f"Product number {position}")
        
        # Source announcement
        source = product.get('source', 'Unknown store')
        description_parts.append(f"from {source}")
        
        # Product title (cleaned for voice)
        title = self.clean_title_for_voice(product.get('title', 'Unknown product'))
        description_parts.append(f"Product name: {title}")
        
        # Price information
        price = product.get('price', 0)
        price_description = self.get_detailed_price_description(price)
        description_parts.append(price_description)
        
        # Rating information
        rating = product.get('rating', 'No rating')
        if rating and rating != 'No rating':
            rating_description = self.describe_rating(rating)
            description_parts.append(rating_description)
        else:
            description_parts.append("Rating information not available")
        
        # Category and feature detection
        category_info = self.detect_product_category(title)
        if category_info:
            description_parts.append(category_info)
        
        # Accessibility features
        accessibility_tips = self.get_accessibility_tips(product)
        if accessibility_tips:
            description_parts.extend(accessibility_tips)
        
        return ". ".join(description_parts) + "."
    
    def clean_title_for_voice(self, title: str) -> str:
        """Clean product title for better voice output"""
        # Remove excessive punctuation and symbols
        title = re.sub(r'[^\w\s\-\(\)]', ' ', title)
        
        # Replace common abbreviations and symbols
        replacements = {
            'mens': "men's",
            'womens': "women's",
            'kids': "children's",
            'xl': 'extra large',
            'lg': 'large',
            'md': 'medium',
            'sm': 'small',
            'xs': 'extra small',
            'ml': 'milliliters',
            'kg': 'kilograms',
            'gm': 'grams',
            'cm': 'centimeters',
            'mm': 'millimeters',
            'led': 'L E D',
            'usb': 'U S B',
            'wifi': 'Wi-Fi',
            'bluetooth': 'Bluetooth',
            '&': 'and',
            '+': 'plus',
            '%': 'percent'
        }
        
        for abbr, full in replacements.items():
            # Escape special regex characters in abbreviations
            escaped_abbr = re.escape(abbr)
            title = re.sub(r'\b' + escaped_abbr + r'\b', full, title, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        title = re.sub(r'\s+', ' ', title).strip()
        
        return title
    
    def get_detailed_price_description(self, price: int) -> str:
        """Generate detailed price description with context"""
        if not price or price <= 0:
            return "Price information not available"
        
        # Format price for voice
        price_text = self.format_price_for_voice(price)
        
        # Add price range context
        price_category = self.categorize_price(price)
        
        # Add comparison context
        comparison = self.get_price_comparison_context(price)
        
        return f"Priced at {price_text}. This is in the {price_category} range. {comparison}"
    
    def format_price_for_voice(self, price: int) -> str:
        """Format price to be voice-friendly"""
        if price >= 100000:
            lakhs = price // 100000
            remainder = price % 100000
            if remainder == 0:
                return f"{lakhs} lakh rupees"
            elif remainder >= 1000:
                thousands = remainder // 1000
                return f"{lakhs} lakh {thousands} thousand rupees"
            else:
                return f"{lakhs} lakh {remainder} rupees"
        elif price >= 1000:
            thousands = price // 1000
            remainder = price % 1000
            if remainder == 0:
                return f"{thousands} thousand rupees"
            else:
                return f"{thousands} thousand {remainder} rupees"
        else:
            return f"{price} rupees"
    
    def categorize_price(self, price: int) -> str:
        """Categorize price into ranges"""
        for category, (min_price, max_price) in self.price_ranges.items():
            if min_price <= price < max_price:
                return category
        return "luxury"
    
    def get_price_comparison_context(self, price: int) -> str:
        """Provide price comparison context"""
        if price < 500:
            return "This is very affordable"
        elif price < 1000:
            return "This is budget-friendly"
        elif price < 5000:
            return "This is reasonably priced"
        elif price < 20000:
            return "This is a mid-range product"
        elif price < 50000:
            return "This is a premium product"
        else:
            return "This is a luxury item"
    
    def describe_rating(self, rating: str) -> str:
        """Describe product rating in detail"""
        try:
            # Extract numeric rating
            rating_match = re.search(r'(\d+\.?\d*)', str(rating))
            if rating_match:
                rating_value = float(rating_match.group(1))
                
                if rating_value >= 4.5:
                    quality = "excellent"
                elif rating_value >= 4.0:
                    quality = "very good"
                elif rating_value >= 3.5:
                    quality = "good"
                elif rating_value >= 3.0:
                    quality = "average"
                else:
                    quality = "below average"
                
                return f"Customer rating: {rating_value} out of 5 stars, which is {quality}"
        except:
            pass
        
        return f"Customer rating: {rating}"
    
    def detect_product_category(self, title: str) -> str:
        """Detect product category and provide relevant information"""
        title_lower = title.lower()
        
        categories = {
            'clothing': {
                'keywords': ['shirt', 'tshirt', 't-shirt', 'top', 'blouse', 'dress', 'pant', 'jean', 'trouser', 'short', 'kurta', 'saree'],
                'info': "This is a clothing item. Consider size, material, and washing instructions"
            },
            'footwear': {
                'keywords': ['shoe', 'sneaker', 'boot', 'sandal', 'slipper', 'heel', 'loafer'],
                'info': "This is footwear. Consider size, comfort, and occasion suitability"
            },
            'electronics': {
                'keywords': ['phone', 'mobile', 'smartphone', 'laptop', 'computer', 'tablet', 'headphone', 'speaker'],
                'info': "This is an electronic device. Check warranty, specifications, and compatibility"
            },
            'books': {
                'keywords': ['book', 'novel', 'guide', 'manual', 'textbook'],
                'info': "This is reading material. Consider format (physical or digital) and language"
            },
            'home': {
                'keywords': ['furniture', 'chair', 'table', 'bed', 'sofa', 'lamp', 'decor'],
                'info': "This is a home item. Consider dimensions, assembly requirements, and room fit"
            },
            'beauty': {
                'keywords': ['cream', 'lotion', 'makeup', 'perfume', 'shampoo', 'soap'],
                'info': "This is a beauty or personal care product. Check ingredients for allergies"
            }
        }
        
        for category, data in categories.items():
            if any(keyword in title_lower for keyword in data['keywords']):
                return data['info']
        
        return "Product category could not be determined automatically"
    
    def get_accessibility_tips(self, product: Dict[str, Any]) -> List[str]:
        """Provide accessibility-specific shopping tips"""
        tips = []
        
        # Source-specific tips
        source = product.get('source', '').lower()
        if 'flipkart' in source:
            tips.append("Flipkart offers easy returns and customer support for accessibility needs")
        elif 'myntra' in source:
            tips.append("Myntra provides detailed size guides and return policies")
        elif 'amazon' in source:
            tips.append("Amazon offers voice shopping through Alexa and detailed product descriptions")
        
        # Price-based tips
        price = product.get('price', 0)
        if price > 10000:
            tips.append("For high-value items, consider reading customer reviews and checking return policies carefully")
        
        return tips
    
    def create_comparison_for_accessibility(self, products: List[Dict[str, Any]]) -> str:
        """Create detailed comparison for multiple products for blind users"""
        if len(products) < 2:
            return "I need at least 2 products to compare."
        
        comparison_parts = [f"Comparing {len(products)} products for you:"]
        
        # Price comparison
        prices = [p.get('price', 0) for p in products if p.get('price', 0) > 0]
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            min_idx = next(i for i, p in enumerate(products) if p.get('price') == min_price)
            max_idx = next(i for i, p in enumerate(products) if p.get('price') == max_price)
            
            comparison_parts.append(f"Price range: from {self.format_price_for_voice(min_price)} to {self.format_price_for_voice(max_price)}")
            comparison_parts.append(f"Most affordable: Product {min_idx + 1} from {products[min_idx].get('source', 'unknown store')}")
            comparison_parts.append(f"Most expensive: Product {max_idx + 1} from {products[max_idx].get('source', 'unknown store')}")
        
        # Source comparison
        sources = [p.get('source', 'Unknown') for p in products]
        unique_sources = list(set(sources))
        if len(unique_sources) > 1:
            comparison_parts.append(f"Products are available from {len(unique_sources)} different stores: {', '.join(unique_sources)}")
        
        # Rating comparison
        rated_products = [p for p in products if p.get('rating') and p.get('rating') != 'No rating']
        if rated_products:
            comparison_parts.append("Rating information available for some products")
        
        # Recommendation
        if prices:
            comparison_parts.append(f"For best value, I recommend considering product {min_idx + 1} as it offers the lowest price")
        
        return ". ".join(comparison_parts) + "."
    
    def create_search_summary_for_accessibility(self, products: List[Dict[str, Any]], query: str) -> str:
        """Create detailed search summary for blind users"""
        if not products:
            return f"I'm sorry, I couldn't find any products matching '{query}'. Try using different keywords or check spelling."
        
        total_count = len(products)
        sources = list(set(p.get('source', 'Unknown') for p in products))
        
        # Price analysis
        prices = [p.get('price', 0) for p in products if p.get('price', 0) > 0]
        price_summary = ""
        if prices:
            min_price = min(prices)
            max_price = max(prices)
            avg_price = sum(prices) // len(prices)
            
            price_summary = f"Prices range from {self.format_price_for_voice(min_price)} to {self.format_price_for_voice(max_price)}, with an average of {self.format_price_for_voice(avg_price)}. "
        
        summary = f"Found {total_count} products for '{query}' from {len(sources)} stores: {', '.join(sources)}. {price_summary}"
        summary += f"Products are sorted by price from lowest to highest. Say 'tell me about item number' followed by a number to get detailed information about any product."
        
        return summary
