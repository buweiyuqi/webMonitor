#!/usr/bin/env python3
"""
Comprehensive Hermès Product Scraper
Captures all products from Hermès website with enhanced selectors
"""

import json
import csv
import re
import time
from datetime import datetime
from typing import List, Dict, Any
import os

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    print("✅ All dependencies available")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Install with: pip3 install selenium webdriver-manager")
    exit(1)

class ComprehensiveHermesScraper:
    def __init__(self):
        self.base_url = "https://www.hermes.com"
        self.category_urls = [
            "https://www.hermes.com/hk/en/category/women/bags-and-small-leather-goods/bags-and-clutches/",
        ]
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with optimal settings"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            return False
    
    def wait_for_content(self, timeout=30):
        """Wait for dynamic content to load"""
        try:
            # Wait for any of these elements to appear
            selectors = [
                '[data-testid="product-tile"]',
                '.product-item',
                '.product-card',
                'article',
                '[class*="product"]'
            ]
            
            for selector in selectors:
                try:
                    WebDriverWait(self.driver, timeout//len(selectors)).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    return True
                except TimeoutException:
                    continue
            
            return False
        except Exception as e:
            print(f"❌ Error waiting for content: {e}")
            return False
    
    def scroll_and_load_all(self):
        """Scroll to load all products"""
        print("📜 Scrolling to load all products...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_attempts = 5
        products_found = 0
        
        while scroll_attempts < max_attempts:
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Count current products
            current_products = len(self.driver.find_elements(By.CSS_SELECTOR, '.product-item, [data-testid="product-tile"], .product-card'))
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height and current_products == products_found:
                break
            
            products_found = current_products
            last_height = new_height
            scroll_attempts += 1
            print(f"   ↳ Scroll {scroll_attempts}: Found {products_found} products")
    
    def extract_all_products(self) -> List[Dict[str, Any]]:
        """Extract all products using comprehensive selectors"""
        products = []
        
        try:
            for url in self.category_urls:
                print(f"🌐 Loading: {url}")
                self.driver.get(url)
                
                # Wait for page to load
                if not self.wait_for_content():
                    print("⚠️  Content not loading, continuing anyway...")
                
                time.sleep(5)  # Additional wait for JavaScript
                
                # Scroll to load all products
                self.scroll_and_load_all()
                
                # Comprehensive selectors for Hermès products
                product_selectors = [
                    '[data-testid="product-tile"]',
                    '.product-item',
                    '.product-card',
                    '.product-tile',
                    'article[data-product-id]',
                    'article.product-item',
                    'article.product-card',
                    '[data-product-id]',
                    '.item-product'
                ]
                
                all_elements = []
                for selector in product_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            all_elements.extend(elements)
                            print(f"   📦 Found {len(elements)} elements with: {selector}")
                    except Exception:
                        continue
                
                # Remove duplicates based on element location
                unique_elements = []
                seen_locations = set()
                for elem in all_elements:
                    try:
                        location = elem.location
                        loc_key = f"{location['x']}_{location['y']}"
                        if loc_key not in seen_locations:
                            seen_locations.add(loc_key)
                            unique_elements.append(elem)
                    except:
                        unique_elements.append(elem)
                
                print(f"🔍 Processing {len(unique_elements)} unique products...")
                
                # Extract product details
                for i, element in enumerate(unique_elements, 1):
                    try:
                        product = self.extract_product_details(element)
                        if product and product.get('name'):
                            products.append(product)
                            print(f"   ✅ {i:3d}. {product['name'][:50]} - HK${product['price']}")
                    except Exception as e:
                        print(f"   ❌ Error with product {i}: {e}")
                        continue
                
        except Exception as e:
            print(f"❌ Critical error: {e}")
        
        return products
    
    def extract_product_details(self, element) -> Dict[str, Any]:
        """Extract detailed product information"""
        product = {
            'name': '',
            'price': '',
            'currency': 'HKD',
            'image_url': '',
            'product_url': '',
            'description': '',
            'availability': 'Available',
            'colors': '',
            'sizes': '',
            'category': 'Bags and Clutches',
            'brand': 'Hermès'
        }
        
        try:
            # Product name - multiple strategies
            name_selectors = [
                '[data-testid="product-title"]',
                '.product-name',
                '.product-title',
                'h3',
                'h2',
                '.item-name',
                'a[href*="/product/"] span',
                '.title'
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    name = name_elem.text.strip()
                    if name and len(name) > 3:
                        product['name'] = name
                        break
                except NoSuchElementException:
                    continue
            
            # Price extraction
            price_selectors = [
                '[data-testid="price"]',
                '.price',
                '.product-price',
                '.current-price',
                'span[class*="price"]',
                '[data-price]'
            ]
            
            for selector in price_selectors:
                try:
                    price_elem = element.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_elem.text.strip()
                    if price_text:
                        # Extract numeric price
                        price_match = re.search(r'[\d,]+', price_text.replace(',', ''))
                        if price_match:
                            product['price'] = price_match.group()
                            if 'HK$' in price_text:
                                product['currency'] = 'HKD'
                            break
                except NoSuchElementException:
                    continue
            
            # Image URL
            try:
                img_selectors = [
                    'img[src*="hermesproduct"]',
                    'img[src*="assets.hermes"]',
                    'img[data-src]',
                    'img',
                    'img[loading="lazy"]'
                ]
                
                for selector in img_selectors:
                    try:
                        img_elem = element.find_element(By.CSS_SELECTOR, selector)
                        img_src = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
                        if img_src:
                            # Ensure full URL
                            if img_src.startswith('//'):
                                img_src = 'https:' + img_src
                            elif img_src.startswith('/'):
                                img_src = self.base_url + img_src
                            product['image_url'] = img_src
                            break
                    except NoSuchElementException:
                        continue
            
            except Exception:
                pass
            
            # Product URL
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, 'a[href*="/product/"]')
                href = link_elem.get_attribute('href')
                if href:
                    product['product_url'] = href if href.startswith('http') else self.base_url + href
            except NoSuchElementException:
                # Try any link within the element
                try:
                    link_elem = element.find_element(By.CSS_SELECTOR, 'a')
                    href = link_elem.get_attribute('href')
                    if href and '/product/' in href:
                        product['product_url'] = href if href.startswith('http') else self.base_url + href
                except NoSuchElementException:
                    pass
            
            # Additional details if available
            try:
                color_elem = element.find_element(By.CSS_SELECTOR, '[data-color], .color')
                product['colors'] = color_elem.text.strip()
            except NoSuchElementException:
                pass
            
            try:
                size_elem = element.find_element(By.CSS_SELECTOR, '[data-size], .size')
                product['sizes'] = size_elem.text.strip()
            except NoSuchElementException:
                pass
            
        except Exception as e:
            print(f"Error extracting details: {e}")
        
        return product if product['name'] else None
    
    def save_results(self, products: List[Dict[str, Any]]):
        """Save results to CSV and JSON"""
        if not products:
            print("❌ No products to save")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f"hermes_products_complete_{timestamp}.csv"
        json_filename = f"hermes_products_complete_{timestamp}.json"
        
        # CSV Export
        fieldnames = [
            'name', 'price', 'currency', 'availability', 'category',
            'description', 'colors', 'sizes', 'brand', 'image_url', 'product_url'
        ]
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)
        
        # JSON Export
        with open(json_filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(products, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"🎉 Results saved:")
        print(f"   📊 CSV: {csv_filename} ({len(products)} products)")
        print(f"   📄 JSON: {json_filename}")
        
        # Show preview
        print(f"\n📋 Sample products:")
        for i, product in enumerate(products[:5], 1):
            print(f"   {i}. {product['name']} - {product['currency']}{product['price']}")
    
    def run(self):
        """Main scraping function"""
        print("🎯 Comprehensive Hermès Product Scraper")
        print("=" * 50)
        
        if not self.setup_driver():
            print("❌ Failed to setup Chrome driver")
            return
        
        try:
            products = self.extract_all_products()
            
            if products:
                self.save_results(products)
                print(f"\n✅ Successfully scraped {len(products)} Hermès products!")
            else:
                print("\n⚠️  No products found")
                print("Possible reasons:")
                print("1. Website structure changed")
                print("2. Products require login")
                print("3. Network issues")
                
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    scraper = ComprehensiveHermesScraper()
    scraper.run()