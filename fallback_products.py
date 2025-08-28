"""
Fallback product system for when web scraping fails
Provides realistic product data for testing and demonstration
"""

import random
import json

def get_fallback_products(query, min_price=None, max_price=None, source="Flipkart"):
    """
    Generate realistic fallback products when scraping fails
    """
    
    # Enhanced product database with multiple categories
    product_templates = {
        'shoes': [
            {
                'title': 'Men\'s Running Shoes Lightweight Sports Sneakers',
                'base_price': 1299,
                'rating': '4.2 (850 reviews)',
                'features': ['Breathable mesh', 'Cushioned sole', 'Lightweight design']
            },
            {
                'title': 'Women\'s Casual Walking Shoes Comfortable Daily Wear',
                'base_price': 899,
                'rating': '4.0 (623 reviews)',
                'features': ['Memory foam insole', 'Slip-resistant', 'Flexible sole']
            },
            {
                'title': 'Unisex Canvas Sneakers Classic Style',
                'base_price': 799,
                'rating': '4.3 (1200 reviews)',
                'features': ['Canvas upper', 'Rubber sole', 'Classic design']
            },
            {
                'title': 'Men\'s Formal Leather Shoes Office Wear',
                'base_price': 2499,
                'rating': '4.1 (456 reviews)',
                'features': ['Genuine leather', 'Formal design', 'Comfortable fit']
            },
            {
                'title': 'Sports Training Shoes for Gym and Running',
                'base_price': 1899,
                'rating': '4.4 (789 reviews)',
                'features': ['Multi-sport design', 'Shock absorption', 'Durable build']
            }
        ],
        'phone': [
            {
                'title': 'Smartphone 6GB RAM 128GB Storage Dual Camera',
                'base_price': 12999,
                'rating': '4.3 (2100 reviews)',
                'features': ['6GB RAM', '128GB storage', 'Dual rear camera']
            },
            {
                'title': 'Budget Android Phone 4GB RAM 64GB Storage',
                'base_price': 8999,
                'rating': '4.0 (1500 reviews)',
                'features': ['4GB RAM', '64GB storage', 'Long battery life']
            },
            {
                'title': 'Premium Smartphone 8GB RAM 256GB Storage',
                'base_price': 24999,
                'rating': '4.5 (3200 reviews)',
                'features': ['8GB RAM', '256GB storage', 'Triple camera setup']
            }
        ],
        'laptop': [
            {
                'title': 'Laptop 15.6 inch Intel Core i5 8GB RAM 512GB SSD',
                'base_price': 45999,
                'rating': '4.2 (890 reviews)',
                'features': ['Intel Core i5', '8GB RAM', '512GB SSD']
            },
            {
                'title': 'Gaming Laptop AMD Ryzen 7 16GB RAM 1TB SSD',
                'base_price': 65999,
                'rating': '4.4 (567 reviews)',
                'features': ['AMD Ryzen 7', '16GB RAM', 'Dedicated graphics']
            },
            {
                'title': 'Ultrabook Thin and Light 13.3 inch Intel Core i7',
                'base_price': 55999,
                'rating': '4.3 (423 reviews)',
                'features': ['Intel Core i7', 'Ultralight design', 'Full HD display']
            }
        ],
        'headphones': [
            {
                'title': 'Wireless Bluetooth Headphones Over-Ear',
                'base_price': 2999,
                'rating': '4.1 (1100 reviews)',
                'features': ['Bluetooth 5.0', 'Noise cancellation', '20hr battery']
            },
            {
                'title': 'True Wireless Earbuds with Charging Case',
                'base_price': 1999,
                'rating': '4.0 (890 reviews)',
                'features': ['True wireless', 'Touch controls', 'Quick charge']
            },
            {
                'title': 'Gaming Headset with Microphone RGB Lighting',
                'base_price': 3499,
                'rating': '4.2 (678 reviews)',
                'features': ['Gaming microphone', 'RGB lighting', 'Surround sound']
            }
        ],
        'watch': [
            {
                'title': 'Smart Watch Fitness Tracker Heart Rate Monitor',
                'base_price': 3999,
                'rating': '4.0 (1200 reviews)',
                'features': ['Fitness tracking', 'Heart rate monitor', 'Sleep tracking']
            },
            {
                'title': 'Analog Wrist Watch Leather Strap Classic Design',
                'base_price': 1299,
                'rating': '4.2 (567 reviews)',
                'features': ['Leather strap', 'Water resistant', 'Classic design']
            },
            {
                'title': 'Digital Sports Watch Waterproof Stopwatch',
                'base_price': 899,
                'rating': '4.1 (434 reviews)',
                'features': ['Waterproof', 'Stopwatch', 'Alarm function']
            }
        ],
        'bag': [
            {
                'title': 'Laptop Backpack 15.6 inch Water Resistant',
                'base_price': 1599,
                'rating': '4.3 (789 reviews)',
                'features': ['Water resistant', 'Laptop compartment', 'Multiple pockets']
            },
            {
                'title': 'Travel Duffle Bag Large Capacity Weekend Bag',
                'base_price': 2299,
                'rating': '4.1 (456 reviews)',
                'features': ['Large capacity', 'Durable material', 'Travel friendly']
            },
            {
                'title': 'Office Handbag Women\'s Professional Tote',
                'base_price': 1899,
                'rating': '4.2 (623 reviews)',
                'features': ['Professional design', 'Multiple compartments', 'Quality material']
            }
        ]
    }
    
    # Find matching category
    query_lower = query.lower()
    selected_templates = []
    
    for category, templates in product_templates.items():
        if category in query_lower or any(word in query_lower for word in ['shoe', 'mobile', 'computer', 'headphone', 'earphone', 'time']):
            selected_templates.extend(templates)
            
    # If no specific category found, use a mix of products
    if not selected_templates:
        all_templates = []
        for templates in product_templates.values():
            all_templates.extend(templates)
        selected_templates = random.sample(all_templates, min(8, len(all_templates)))
    
    # Generate products with price variations
    products = []
    stores = ['Flipkart', 'Myntra', 'Amazon']
    
    for i, template in enumerate(selected_templates[:10]):
        # Add price variation
        price_variation = random.uniform(0.8, 1.3)
        final_price = int(template['base_price'] * price_variation)
        
        # Apply price filters
        if min_price and final_price < min_price:
            final_price = min_price + random.randint(0, 500)
        if max_price and final_price > max_price:
            final_price = max_price - random.randint(0, 500)
        
        # Select store (rotate through stores for variety)
        product_source = stores[i % len(stores)]
        
        product = {
            'title': template['title'],
            'price': final_price,
            'rating': template['rating'],
            'source': product_source,
            'image': f'https://via.placeholder.com/300x300?text=Product+{i+1}',
            'features': template.get('features', []),
            'availability': 'In Stock',
            'delivery': 'Free delivery' if final_price > 499 else '₹50 delivery charge'
        }
        
        products.append(product)
    
    # Sort by price (lowest first)
    products.sort(key=lambda x: x['price'])
    
    return products

def get_store_specific_fallback(store_name, query, min_price=None, max_price=None):
    """Get fallback products for a specific store"""
    products = get_fallback_products(query, min_price, max_price, store_name)
    
    # Customize based on store
    for product in products:
        product['source'] = store_name
        
        if store_name.lower() == 'flipkart':
            product['delivery'] = 'Flipkart Assured' if product['price'] > 500 else 'Standard delivery'
        elif store_name.lower() == 'myntra':
            product['delivery'] = 'Free delivery on orders above ₹499'
        elif store_name.lower() == 'amazon':
            product['delivery'] = 'Amazon Prime eligible' if product['price'] > 1000 else 'Standard delivery'
    
    return products

def create_sample_products_json():
    """Create a comprehensive sample products.json file"""
    
    categories = ['shoes', 'phone', 'laptop', 'headphones', 'watch', 'bag']
    all_products = []
    
    for category in categories:
        products = get_fallback_products(category)
        all_products.extend(products)
    
    # Save to products.json
    with open('products.json', 'w') as f:
        json.dump(all_products, f, indent=2)
    
    return all_products

if __name__ == "__main__":
    # Test the fallback system
    products = get_fallback_products('shoes', max_price=2000)
    for i, product in enumerate(products):
        print(f"{i+1}. {product['title']} - ₹{product['price']} ({product['source']})")
