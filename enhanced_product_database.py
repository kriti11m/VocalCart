import json
import random
from typing import List, Dict, Any
import re

class EnhancedProductDatabase:
    """
    Comprehensive product database for VocalCart with real-world product data
    Serves as an intelligent fallback when web scraping fails
    Designed specifically for accessibility and blind users
    """
    
    def __init__(self):
        self.categories = {
            'footwear': {
                'keywords': ['shoes', 'sneakers', 'sandals', 'boots', 'slippers', 'heels', 'flats', 'loafers'],
                'products': [
                    {'title': 'Nike Air Max 270 Running Shoes', 'price': 8999, 'rating': '4.3', 'source': 'Flipkart', 'category': 'Sports Shoes'},
                    {'title': 'Adidas Ultraboost 22 Black', 'price': 15999, 'rating': '4.5', 'source': 'Myntra', 'category': 'Running Shoes'},
                    {'title': 'Puma RS-X3 Puzzle White Sneakers', 'price': 6799, 'rating': '4.2', 'source': 'Amazon', 'category': 'Casual Shoes'},
                    {'title': 'Bata Formal Black Leather Shoes', 'price': 2499, 'rating': '4.0', 'source': 'Flipkart', 'category': 'Formal Shoes'},
                    {'title': 'Crocs Classic Clog Comfortable Sandals', 'price': 3295, 'rating': '4.4', 'source': 'Amazon', 'category': 'Sandals'},
                    {'title': 'Woodland Leather Boots Brown', 'price': 4999, 'rating': '4.1', 'source': 'Myntra', 'category': 'Boots'},
                    {'title': 'Sparx Mens Running Shoes Navy Blue', 'price': 1899, 'rating': '3.9', 'source': 'Flipkart', 'category': 'Sports Shoes'},
                    {'title': 'Campus North Plus White Sneakers', 'price': 1299, 'rating': '4.2', 'source': 'Amazon', 'category': 'Casual Shoes'},
                    {'title': 'Red Tape Casual Loafers Tan Brown', 'price': 2799, 'rating': '4.0', 'source': 'Myntra', 'category': 'Loafers'},
                    {'title': 'Liberty Force 10 Sports Shoes Black', 'price': 999, 'rating': '3.8', 'source': 'Flipkart', 'category': 'Sports Shoes'}
                ]
            },
            'clothing': {
                'keywords': ['shirt', 'tshirt', 't-shirt', 'top', 'dress', 'jeans', 'pants', 'kurta', 'saree', 'blouse'],
                'products': [
                    {'title': 'Levis 511 Slim Fit Jeans Dark Blue', 'price': 3999, 'rating': '4.4', 'source': 'Myntra', 'category': 'Jeans'},
                    {'title': 'H&M Cotton Basic T-Shirt White', 'price': 799, 'rating': '4.1', 'source': 'Amazon', 'category': 'T-Shirts'},
                    {'title': 'Allen Solly Formal Shirt Light Blue', 'price': 1899, 'rating': '4.2', 'source': 'Flipkart', 'category': 'Formal Shirts'},
                    {'title': 'Zara Floral Summer Dress', 'price': 2999, 'rating': '4.3', 'source': 'Myntra', 'category': 'Dresses'},
                    {'title': 'United Colors of Benetton Polo T-Shirt', 'price': 1499, 'rating': '4.0', 'source': 'Amazon', 'category': 'Polo Shirts'},
                    {'title': 'Fabindia Cotton Kurta Cream', 'price': 1799, 'rating': '4.5', 'source': 'Flipkart', 'category': 'Ethnic Wear'},
                    {'title': 'Nike Dri-FIT Sports T-Shirt Black', 'price': 1999, 'rating': '4.3', 'source': 'Amazon', 'category': 'Sports Wear'},
                    {'title': 'Van Heusen Formal Trousers Grey', 'price': 2499, 'rating': '4.1', 'source': 'Myntra', 'category': 'Formal Pants'},
                    {'title': 'Roadster Denim Jacket Blue', 'price': 1899, 'rating': '4.2', 'source': 'Flipkart', 'category': 'Jackets'},
                    {'title': 'Forever 21 Graphic Print T-Shirt', 'price': 699, 'rating': '3.9', 'source': 'Myntra', 'category': 'Casual Wear'}
                ]
            },
            'electronics': {
                'keywords': ['phone', 'mobile', 'smartphone', 'laptop', 'tablet', 'headphones', 'earphones', 'speaker', 'charger'],
                'products': [
                    {'title': 'Samsung Galaxy S24 Ultra 256GB Titanium', 'price': 124999, 'rating': '4.6', 'source': 'Amazon', 'category': 'Smartphones'},
                    {'title': 'Apple iPhone 15 Pro Max 256GB Natural Titanium', 'price': 159900, 'rating': '4.7', 'source': 'Flipkart', 'category': 'Smartphones'},
                    {'title': 'OnePlus 12 5G 256GB Flowy Emerald', 'price': 64999, 'rating': '4.5', 'source': 'Myntra', 'category': 'Smartphones'},
                    {'title': 'MacBook Air M3 13-inch 256GB Space Grey', 'price': 114900, 'rating': '4.8', 'source': 'Amazon', 'category': 'Laptops'},
                    {'title': 'Dell Inspiron 15 3000 Intel i5 8GB RAM', 'price': 45990, 'rating': '4.2', 'source': 'Flipkart', 'category': 'Laptops'},
                    {'title': 'Sony WH-1000XM5 Wireless Noise Canceling Headphones', 'price': 29990, 'rating': '4.6', 'source': 'Amazon', 'category': 'Headphones'},
                    {'title': 'Apple AirPods Pro 2nd Generation', 'price': 24900, 'rating': '4.5', 'source': 'Flipkart', 'category': 'Earphones'},
                    {'title': 'JBL Flip 6 Portable Bluetooth Speaker Blue', 'price': 9999, 'rating': '4.4', 'source': 'Amazon', 'category': 'Speakers'},
                    {'title': 'Samsung Galaxy Tab S9 11-inch 128GB', 'price': 76999, 'rating': '4.3', 'source': 'Myntra', 'category': 'Tablets'},
                    {'title': 'Anker PowerCore 20000mAh Power Bank', 'price': 2999, 'rating': '4.4', 'source': 'Flipkart', 'category': 'Accessories'}
                ]
            },
            'home': {
                'keywords': ['furniture', 'chair', 'table', 'bed', 'sofa', 'lamp', 'cushion', 'curtain', 'rug', 'decor'],
                'products': [
                    {'title': 'IKEA HEMNES Bed Frame White Double Bed', 'price': 18999, 'rating': '4.3', 'source': 'Amazon', 'category': 'Furniture'},
                    {'title': 'Urban Ladder Winger 2 Seater Sofa Grey', 'price': 24999, 'rating': '4.4', 'source': 'Flipkart', 'category': 'Sofas'},
                    {'title': 'Study Table with Drawer Engineered Wood', 'price': 8999, 'rating': '4.1', 'source': 'Myntra', 'category': 'Tables'},
                    {'title': 'Godrej Interio Office Chair Ergonomic', 'price': 12999, 'rating': '4.2', 'source': 'Amazon', 'category': 'Chairs'},
                    {'title': 'Philips LED Table Lamp Adjustable', 'price': 2499, 'rating': '4.0', 'source': 'Flipkart', 'category': 'Lighting'},
                    {'title': 'Cotton Printed Cushion Covers Set of 5', 'price': 899, 'rating': '4.1', 'source': 'Amazon', 'category': 'Home Decor'},
                    {'title': 'Blackout Curtains Door 7 Feet Brown', 'price': 1499, 'rating': '3.9', 'source': 'Myntra', 'category': 'Curtains'},
                    {'title': 'Carpet Living Room Large Size 6x4 Feet', 'price': 3999, 'rating': '4.2', 'source': 'Flipkart', 'category': 'Carpets'},
                    {'title': 'Wall Clock Analog Designer Wooden', 'price': 799, 'rating': '4.0', 'source': 'Amazon', 'category': 'Wall Decor'},
                    {'title': 'Kitchen Storage Container Set Plastic', 'price': 1299, 'rating': '4.1', 'source': 'Myntra', 'category': 'Storage'}
                ]
            },
            'beauty': {
                'keywords': ['cream', 'lotion', 'makeup', 'perfume', 'shampoo', 'soap', 'skincare', 'cosmetics'],
                'products': [
                    {'title': 'Lakme Absolute Perfect Radiance Foundation', 'price': 1350, 'rating': '4.2', 'source': 'Myntra', 'category': 'Makeup'},
                    {'title': 'Himalaya Herbals Face Wash Neem', 'price': 145, 'rating': '4.3', 'source': 'Amazon', 'category': 'Skincare'},
                    {'title': 'Neutrogena Ultra Sheer Sunscreen SPF 50', 'price': 599, 'rating': '4.4', 'source': 'Flipkart', 'category': 'Sunscreen'},
                    {'title': 'LOreal Paris Revitalift Anti-Aging Cream', 'price': 999, 'rating': '4.1', 'source': 'Amazon', 'category': 'Anti-Aging'},
                    {'title': 'Dove Intense Repair Shampoo 650ml', 'price': 299, 'rating': '4.2', 'source': 'Flipkart', 'category': 'Hair Care'},
                    {'title': 'Fogg Fresh Deodorant Body Spray for Men', 'price': 399, 'rating': '4.0', 'source': 'Myntra', 'category': 'Deodorants'},
                    {'title': 'Plum Green Tea Face Wash Oil Control', 'price': 345, 'rating': '4.3', 'source': 'Amazon', 'category': 'Face Wash'},
                    {'title': 'Maybelline New York Fit Me Foundation', 'price': 699, 'rating': '4.1', 'source': 'Flipkart', 'category': 'Foundation'},
                    {'title': 'The Body Shop Vitamin E Moisturizer', 'price': 1695, 'rating': '4.4', 'source': 'Myntra', 'category': 'Moisturizer'},
                    {'title': 'Garnier Micellar Cleansing Water', 'price': 399, 'rating': '4.2', 'source': 'Amazon', 'category': 'Cleansing Water'}
                ]
            },
            'books': {
                'keywords': ['book', 'novel', 'textbook', 'guide', 'fiction', 'non-fiction', 'autobiography'],
                'products': [
                    {'title': 'Rich Dad Poor Dad by Robert Kiyosaki', 'price': 295, 'rating': '4.5', 'source': 'Amazon', 'category': 'Finance'},
                    {'title': 'The Alchemist by Paulo Coelho', 'price': 199, 'rating': '4.6', 'source': 'Flipkart', 'category': 'Fiction'},
                    {'title': 'Atomic Habits by James Clear', 'price': 399, 'rating': '4.7', 'source': 'Myntra', 'category': 'Self-Help'},
                    {'title': 'Think and Grow Rich by Napoleon Hill', 'price': 150, 'rating': '4.4', 'source': 'Amazon', 'category': 'Motivational'},
                    {'title': 'The Power of Your Subconscious Mind', 'price': 175, 'rating': '4.3', 'source': 'Flipkart', 'category': 'Psychology'},
                    {'title': 'NCERT Physics Class 12 Textbook', 'price': 695, 'rating': '4.2', 'source': 'Amazon', 'category': 'Educational'},
                    {'title': 'Harry Potter Complete Book Set', 'price': 2499, 'rating': '4.8', 'source': 'Myntra', 'category': 'Fantasy'},
                    {'title': 'The Mahabharata A Modern Rendering', 'price': 599, 'rating': '4.1', 'source': 'Flipkart', 'category': 'Mythology'},
                    {'title': 'Sapiens by Yuval Noah Harari', 'price': 449, 'rating': '4.5', 'source': 'Amazon', 'category': 'History'},
                    {'title': 'The Intelligent Investor by Benjamin Graham', 'price': 599, 'rating': '4.4', 'source': 'Flipkart', 'category': 'Investment'}
                ]
            }
        }
        
        # Price ranges for filtering
        self.price_ranges = {
            'under_500': (0, 500),
            'under_1000': (0, 1000),
            'under_2000': (0, 2000),
            'under_5000': (0, 5000),
            'under_10000': (0, 10000),
            'under_20000': (0, 20000),
            'above_20000': (20000, float('inf'))
        }
    
    def search_products(self, query: str, min_price: int = None, max_price: int = None) -> List[Dict[str, Any]]:
        """
        Intelligent product search with category detection and price filtering
        Designed for accessibility with comprehensive product information
        """
        query_lower = query.lower()
        matched_products = []
        
        # Detect category based on keywords
        detected_categories = []
        for category, data in self.categories.items():
            if any(keyword in query_lower for keyword in data['keywords']):
                detected_categories.append(category)
        
        # If no specific category detected, search all categories
        if not detected_categories:
            detected_categories = list(self.categories.keys())
        
        # Collect products from detected categories
        for category in detected_categories:
            products = self.categories[category]['products']
            category_keywords = self.categories[category]['keywords']
            
            # Filter by keywords in product title or category match
            for product in products:
                title_lower = product['title'].lower()
                should_include = False
                
                # Check if any word from query appears in title
                query_words = query_lower.split()
                if any(word in title_lower for word in query_words if len(word) > 2):
                    should_include = True
                
                # Also include if query matches category keywords and we're in that category
                elif any(keyword in query_lower for keyword in category_keywords):
                    should_include = True
                
                if should_include:
                    product_copy = product.copy()
                    product_copy['search_relevance'] = self._calculate_relevance(query_lower, title_lower, category_keywords)
                    matched_products.append(product_copy)
        
        # Filter by price range
        if min_price is not None or max_price is not None:
            filtered_products = []
            for product in matched_products:
                price = product.get('price', 0)
                if min_price is not None and price < min_price:
                    continue
                if max_price is not None and price > max_price:
                    continue
                filtered_products.append(product)
            matched_products = filtered_products
        
        # Sort by relevance and price
        matched_products.sort(key=lambda x: (-x.get('search_relevance', 0), x.get('price', 0)))
        
        # Add variety by shuffling products with same relevance
        self._add_variety(matched_products)
        
        return matched_products[:15]  # Return top 15 results
    
    def _calculate_relevance(self, query: str, title: str, category_keywords: List[str] = None) -> float:
        """Calculate search relevance score"""
        query_words = set(query.split())
        title_words = set(title.split())
        
        # Exact matches get higher score
        exact_matches = len(query_words.intersection(title_words))
        
        # Partial matches
        partial_matches = 0
        for q_word in query_words:
            for t_word in title_words:
                if q_word in t_word or t_word in q_word:
                    partial_matches += 0.5
        
        # Category keyword bonus - if query matches category keywords, give bonus
        category_bonus = 0
        if category_keywords:
            for keyword in category_keywords:
                if keyword in query.lower():
                    category_bonus += 1
        
        return exact_matches + partial_matches + category_bonus
    
    def _add_variety(self, products: List[Dict]) -> None:
        """Add variety by ensuring different stores are represented"""
        if len(products) <= 5:
            return
        
        # Group by store
        store_groups = {}
        for i, product in enumerate(products):
            store = product.get('source', 'Unknown')
            if store not in store_groups:
                store_groups[store] = []
            store_groups[store].append((i, product))
        
        # Redistribute to ensure variety
        result = []
        max_per_store = max(2, len(products) // len(store_groups))
        
        for store, items in store_groups.items():
            result.extend([item[1] for item in items[:max_per_store]])
        
        # Add remaining products
        used_indices = set()
        for store, items in store_groups.items():
            for i, (original_index, product) in enumerate(items):
                if i < max_per_store:
                    used_indices.add(original_index)
        
        for i, product in enumerate(products):
            if i not in used_indices and len(result) < len(products):
                result.append(product)
        
        products[:] = result
    
    def get_category_suggestions(self, query: str) -> List[str]:
        """Get category suggestions based on query"""
        query_lower = query.lower()
        suggestions = []
        
        for category, data in self.categories.items():
            if any(keyword in query_lower for keyword in data['keywords']):
                suggestions.append(category.replace('_', ' ').title())
        
        return suggestions or ['Electronics', 'Clothing', 'Footwear', 'Home & Decor']
    
    def get_product_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        total_products = sum(len(cat['products']) for cat in self.categories.values())
        return {
            'total_products': total_products,
            'categories': len(self.categories),
            'stores': len(set(p['source'] for cat in self.categories.values() for p in cat['products']))
        }
    
    def get_trending_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending products (high rating products from all categories)"""
        all_products = []
        for category_data in self.categories.values():
            all_products.extend(category_data['products'])
        
        # Sort by rating and add some randomness
        trending = sorted(all_products, key=lambda x: (float(x.get('rating', 0)), random.random()), reverse=True)
        return trending[:limit]
