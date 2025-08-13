#!/usr/bin/env python3
"""
Hermès Test Server
A simple Flask server that simulates Hermès product catalog with dynamic updates
Perfect for testing the monitoring service
"""

from flask import Flask, render_template_string, jsonify
import random
import time
from datetime import datetime
import threading
import json

app = Flask(__name__)

# Test products that will dynamically change
products = [
    {"name": "Birkin 25 bag", "price": 85000, "currency": "HKD", "sku": "H123456", "image": "birkin.jpg"},
    {"name": "Kelly 28 bag", "price": 78000, "currency": "HKD", "sku": "H234567", "image": "kelly.jpg"},
    {"name": "Picotin Lock 18 bag", "price": 28200, "currency": "HKD", "sku": "H345678", "image": "picotin.jpg"},
    {"name": "Roulis mini bag", "price": 71500, "currency": "HKD", "sku": "H456789", "image": "roulis.jpg"},
    {"name": "Constance 18 bag", "price": 65000, "currency": "HKD", "sku": "H567890", "image": "constance.jpg"},
    {"name": "Evelyne TPM bag", "price": 25000, "currency": "HKD", "sku": "H678901", "image": "evelyne.jpg"},
    {"name": "Garden Party 30 bag", "price": 35000, "currency": "HKD", "sku": "H789012", "image": "garden.jpg"},
    {"name": "Bolide 27 bag", "price": 58000, "currency": "HKD", "sku": "H890123", "image": "bolide.jpg"}
]

# Dynamic products that will appear/disappear
dynamic_products = []

def generate_dynamic_products():
    """Generate random products that appear/disappear"""
    test_products = [
        {"name": "Limited Edition Birkin 30", "price": 120000, "currency": "HKD", "sku": "L001", "image": "limited_birkin.jpg"},
        {"name": "Kelly Sellier 25", "price": 82000, "currency": "HKD", "sku": "L002", "image": "kelly_sellier.jpg"},
        {"name": "Picotin Lock 22", "price": 32000, "currency": "HKD", "sku": "L003", "image": "picotin_22.jpg"},
        {"name": "Roulis 23 bag", "price": 78000, "currency": "HKD", "sku": "L004", "image": "roulis_23.jpg"},
        {"name": "Special Kelly 32", "price": 95000, "currency": "HKD", "sku": "L005", "image": "special_kelly.jpg"}
    ]
    
    while True:
        # Randomly add/remove products
        if len(dynamic_products) < 3 and random.random() < 0.3:
            new_product = random.choice(test_products).copy()
            new_product["id"] = f"dynamic_{int(time.time())}"
            new_product["timestamp"] = datetime.now().isoformat()
            dynamic_products.append(new_product)
            print(f"🆕 Added: {new_product['name']}")
        
        elif len(dynamic_products) > 0 and random.random() < 0.2:
            removed = dynamic_products.pop(0)
            print(f"❌ Removed: {removed['name']}")
        
        time.sleep(10)  # Change every 10 seconds

# Start background thread for dynamic changes
threading.Thread(target=generate_dynamic_products, daemon=True).start()

@app.route('/')
def index():
    """Main page simulating Hermès website"""
    html = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hermès Test Store - Bags & Clutches</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .header { text-align: center; margin-bottom: 30px; }
            .products { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .product-card {
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                transition: transform 0.3s;
            }
            .product-card:hover { transform: translateY(-5px); }
            .product-image {
                width: 100%;
                height: 200px;
                background: #eee;
                border-radius: 4px;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #666;
            }
            .product-name { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
            .product-price { font-size: 20px; color: #d4af37; margin-bottom: 10px; }
            .product-sku { font-size: 12px; color: #666; }
            .product-link { color: #d4af37; text-decoration: none; }
            .dynamic-badge {
                background: #ff4757;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Hermès Test Store</h1>
            <p>Women's Bags & Clutches</p>
            <p>🧪 This is a test server for monitoring service</p>
            <p>📊 Products change every 10-30 seconds</p>
        </div>
        
        <div class="products" id="products">
            {% for product in products %}
            <div class="product-card" data-product-id="{{ product.sku }}">
                <div class="product-image">{{ product.name[:15] }}</div>
                <div class="product-name">
                    {{ product.name }}
                    {% if product.name.startswith('Limited') or product.name.startswith('Special') %}
                        <span class="dynamic-badge">NEW</span>
                    {% endif %}
                </div>
                <div class="product-price">HK${{ "{:,}".format(product.price) }}</div>
                <div class="product-sku">SKU: {{ product.sku }}</div>
                <a href="/product/{{ product.sku }}" class="product-link">View Details</a>
            </div>
            {% endfor %}
        </div>
        
        <div id="dynamic-products" style="margin-top: 30px;">
            <h2>🔄 Dynamic Products (Appear/Disappear)</h2>
            {% for product in dynamic_products %}
            <div class="product-card" style="border-left: 4px solid #ff4757;">
                <div class="product-image">{{ product.name[:15] }}</div>
                <div class="product-name">{{ product.name }} <span class="dynamic-badge">DYNAMIC</span></div>
                <div class="product-price">HK${{ "{:,}".format(product.price) }}</div>
                <div class="product-sku">SKU: {{ product.sku }}</div>
                <div style="font-size: 12px; color: #666;">Added: {{ product.timestamp[:19] }}</div>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    '''
    
    all_products = products + dynamic_products
    return render_template_string(html, products=products, dynamic_products=dynamic_products)

@app.route('/api/products')
def api_products():
    """API endpoint returning products in JSON format for monitoring"""
    all_products = products + dynamic_products
    return jsonify({
        "products": all_products,
        "timestamp": datetime.now().isoformat(),
        "total_count": len(all_products),
        "dynamic_count": len(dynamic_products)
    })

@app.route('/api/dynamic-products')
def api_dynamic_products():
    """API endpoint for just dynamic products"""
    return jsonify({
        "products": dynamic_products,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/test-monitor')
def test_monitor():
    """Test page for monitoring service"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Monitor Interface</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; }
            .info { background: #d1ecf1; color: #0c5460; }
            .products { margin: 20px 0; }
            .product { padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>🧪 Hermès Monitoring Service Test</h1>
        
        <div class="status success">
            ✅ Test server is running!
        </div>
        
        <div class="info">
            📊 Products are changing dynamically every 10-30 seconds
        </div>
        
        <div class="info">
            🔗 API Endpoints:<br>
            <a href="/api/products">/api/products</a> - All products<br>
            <a href="/api/dynamic-products">/api/dynamic-products</a> - Only dynamic products
        </div>
        
        <h2>📦 Current Products:</h2>
        <div id="products"></div>
        
        <script>
        function loadProducts() {
            fetch('/api/products')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('products');
                    container.innerHTML = '';
                    data.products.forEach(product => {
                        const div = document.createElement('div');
                        div.className = 'product';
                        div.innerHTML = `
                            <strong>${product.name}</strong> - HK$${product.price.toLocaleString()}
                            <br>
                            <small>SKU: ${product.sku}</small>
                        `;
                        container.appendChild(div);
                    });
                });
        }
        
        // Reload every 15 seconds
        loadProducts();
        setInterval(loadProducts, 15000);
        </script>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    print("🧪 Starting Hermès Test Server...")
    print("📱 Main page: http://localhost:5001")
    print("📊 API: http://localhost:5001/api/products")
    print("🧪 Test: http://localhost:5001/test-monitor")
    print("🔄 Products change every 10-30 seconds")
    app.run(debug=True, host='0.0.0.0', port=5001)