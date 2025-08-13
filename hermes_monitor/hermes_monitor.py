#!/usr/bin/env python3
"""
Hermès Product Monitoring Service
Continuously monitors Hermès website for new products and sends email notifications
"""

import json
import csv
import re
import time
import os
import smtplib
from loguru import logger
import traceback
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Set

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

class HermesMonitor:
    def __init__(self, config_file="config.json"):
        self.config = self.load_config(config_file)
        self.result_dir = "../result"
        self.last_products_file = self.config["storage"]["last_products_file"]
        self.log_file = self.config["storage"]["log_file"]
        
        # Setup logging
        self.setup_logging()
        self.logger = logger
        
        # Create directories
        os.makedirs(self.result_dir, exist_ok=True)
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Config file {config_file} not found")
            exit(1)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in {config_file}")
            exit(1)
    
    def setup_logging(self):
        """Setup logging configuration"""
        logger.add(sink=self.log_file, level="INFO")
    
    def setup_driver(self):
        """Setup Chrome driver for monitoring"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            self.logger.error(f"Driver setup failed: {e}")
            return None
    
    def scrape_current_products(self) -> List[Dict[str, Any]]:
        """Scrape current products from website"""
        driver = self.setup_driver()
        if not driver:
            return []
        
        products = []
        
        try:
            for url in self.config["monitoring"]["urls"]:
                self.logger.info(f"Scraping: {url}")
                driver.get(url)
                
                # Wait for page load
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except TimeoutException:
                    self.logger.warning("Page load timeout")
                    continue
                
                time.sleep(3)  # Allow JS to load
                
                # Load all products via scroll
                page_products = self.load_all_products(driver)
                products.extend(page_products)
                
        except Exception as e:
            self.logger.error(f"Scraping error: {e}")
        finally:
            if driver:
                driver.quit()
        
        return products
    
    def load_all_products(self, driver) -> List[Dict[str, Any]]:
        """Load all products from current page"""
        products = []
        seen_products = set()
        
        scroll_attempts = 0
        max_attempts = 8
        
        while scroll_attempts < max_attempts:
            # Get current products
            current_products = self.extract_products_from_page(driver)
            
            # Add new unique products
            for product in current_products:
                product_key = f"{product.get('name', '')}_{product.get('price', '')}"
                if product_key not in seen_products and product.get('name'):
                    seen_products.add(product_key)
                    products.append(product)
            
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            scroll_attempts += 1
        
        return products
    
    def extract_products_from_page(self, driver) -> List[Dict[str, Any]]:
        """Extract products from current page state"""
        products = []
        
        # Comprehensive selectors
        selectors = [
            '[data-testid="product-tile"]',
            '.product-item',
            '.product-card',
            'article[data-product-id]',
            'article.product-item',
            'article'
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    product = self.extract_product_details(element, driver)
                    if product and product.get('name'):
                        products.append(product)
                break
            except Exception as e:
                continue
        
        return products
    
    def extract_product_details(self, element, driver):
        """Extract product details from element"""
        product = {
            'name': '',
            'price': '',
            'currency': 'HKD',
            'image_url': '',
            'product_url': '',
            'sku': '',
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Product name
            name_selectors = [
                '.product-name', '.product-title', 'h3', 'h2',
                '[data-testid="product-title"]', '.item-name'
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    name = name_elem.text.strip()
                    if name and len(name) > 3:
                        product['name'] = name
                        break
                except:
                    continue
            
            # Price
            price_selectors = [
                '.price', '.product-price', '[data-price]',
                '.current-price', '.amount'
            ]
            
            for selector in price_selectors:
                try:
                    price_elem = element.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_elem.text.strip()
                    if price_text:
                        price_match = re.search(r'[\d,]+', price_text.replace(',', ''))
                        if price_match:
                            product['price'] = price_match.group()
                        break
                except:
                    continue
            
            # Image URL
            try:
                img_elem = element.find_element(By.CSS_SELECTOR, 'img')
                img_src = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
                if img_src:
                    if img_src.startswith('//'):
                        img_src = 'https:' + img_src
                    elif img_src.startswith('/'):
                        img_src = "https://www.hermes.com" + img_src
                    product['image_url'] = img_src
            except:
                pass
            
            # Product URL
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, 'a[href*="/product/"]')
                href = link_elem.get_attribute('href')
                if href:
                    product['product_url'] = href if href.startswith('http') else "https://www.hermes.com" + href
                    
                    # Extract SKU from URL
                    sku_match = re.search(r'H[A-Z0-9]+', href)
                    if sku_match:
                        product['sku'] = sku_match.group()
            except:
                pass
            
        except Exception as e:
            self.logger.debug(f"Error extracting details: {e}")
        
        return product if product['name'] else None
    
    def load_last_products(self) -> Set[str]:
        """Load previously seen products"""
        try:
            if os.path.exists(self.last_products_file):
                with open(self.last_products_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('products', []))
        except Exception as e:
            self.logger.error(f"Error loading last products: {e}")
        return set()
    
    def save_last_products(self, products: List[Dict[str, Any]]):
        """Save current products for next comparison"""
        try:
            product_keys = [f"{p['name']}_{p['price']}" for p in products]
            data = {
                'products': list(product_keys),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.last_products_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving last products: {e}")
    
    def check_watchlist(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check if products match watchlist criteria"""
        matched = []
        
        for product in products:
            name = product.get('name', '').lower()
            price_str = product.get('price', '0')
            
            try:
                price = int(price_str.replace(',', '')) if price_str.isdigit() else 0
            except:
                price = 0
            
            for watch_item in self.config["watchlist"]["products"]:
                name_match = watch_item["name_contains"].lower() in name
                price_match = watch_item["min_price"] <= price <= watch_item["max_price"]
                
                if name_match and price_match:
                    product['watch_reason'] = f"{watch_item['name_contains']} in range HK${watch_item['min_price']}-{watch_item['max_price']}"
                    matched.append(product)
                    break
        
        return matched
    
    def send_email_notification(self, new_products: List[Dict[str, Any]], matched_products: List[Dict[str, Any]]):
        """Send email notification"""
        if not new_products and not matched_products:
            return
        
        try:
            email_config = self.config["email"]
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_config["sender_email"]
            msg['To'] = ', '.join(email_config["recipient_emails"])
            
            subject_parts = []
            if new_products:
                subject_parts.append(f"{len(new_products)} new products")
            if matched_products:
                subject_parts.append(f"{len(matched_products)} watchlist matches")
            
            msg['Subject'] = f"{email_config['subject_prefix']} {' + '.join(subject_parts)}"
            
            # Create email body
            body = f"""
Hermès Product Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

"""
            
            if new_products:
                body += f"📦 NEW PRODUCTS ({len(new_products)}):"
                for product in new_products[:10]:  # Limit to first 10
                    body += f"   • {product['name']} - HK${product['price']}\n"
                    body += f"     {product['product_url']}\n\n"
            
            if matched_products:
                body += f"🎯 WATCHLIST MATCHES ({len(matched_products)}):"
                for product in matched_products:
                    body += f"   • {product['name']} - HK${product['price']}\n"
                    body += f"     Reason: {product['watch_reason']}\n"
                    body += f"     {product['product_url']}\n\n"
            
            if len(new_products) > 10:
                body += f"... and {len(new_products) - 10} more products\n"
            
            body += f"\n📊 Total products found: {len(new_products)}"
            body += f"\n📁 Full report: {self.result_dir}/"
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # Send email
            server = smtplib.SMTP_SSL(email_config["smtp_server"], port=email_config["smtp_port"])
            # server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            # server.starttls()
            server.login(email_config["sender_email"], email_config["sender_password"])
            
            text = msg.as_string()
            server.sendmail(email_config["sender_email"], email_config["recipient_emails"], text)
            server.quit()
            
            self.logger.info(f"📧 Email sent: {len(new_products)} new, {len(matched_products)} matches")
            
        except Exception as e:
            traceback.print_exc()
            self.logger.error(f"Email send failed: {e}")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        self.logger.info("🚀 Starting Hermès monitoring service...")
        
        last_products = self.load_last_products()
        
        while True:
            try:
                self.logger.info(f"🔍 Checking for new products... ({datetime.now()})")
                
                # Scrape current products
                current_products = self.scrape_current_products()
                
                if not current_products:
                    self.logger.warning("❌ No products found in this scan")
                    time.sleep(self.config["monitoring"]["check_interval_minutes"] * 60)
                    continue
                
                # Find new products
                current_keys = {f"{p['name']}_{p['price']}" for p in current_products}
                new_products = [p for p in current_products if f"{p['name']}_{p['price']}" not in last_products]
                
                # Check watchlist
                matched_products = self.check_watchlist(current_products)
                
                if new_products or matched_products:
                    self.logger.info(f"🎉 Found {len(new_products)} new products, {len(matched_products)} matches")
                    
                    # Send notifications
                    self.send_email_notification(new_products, matched_products)
                    
                    # Save current scan
                    self.save_last_products(current_products)
                    
                    # Save detailed report
                    self.save_monitoring_report(current_products, new_products, matched_products)
                else:
                    self.logger.info("✅ No changes detected")
                
                last_products = current_keys
                
                # Wait for next check
                interval = self.config["monitoring"]["check_interval_minutes"] * 60
                self.logger.info(f"⏳ Next check in {self.config['monitoring']['check_interval_minutes']} minutes")
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def save_monitoring_report(self, all_products, new_products, matched_products):
        """Save detailed monitoring report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = os.path.join(self.result_dir, f"monitoring_report_{timestamp}.json")
        
        report = {
            "scan_time": datetime.now().isoformat(),
            "total_products": len(all_products),
            "new_products": len(new_products),
            "matched_products": len(matched_products),
            "all_products": all_products,
            "new_products_details": new_products,
            "matched_products_details": matched_products
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📄 Report saved: {report_file}")
    
    def run_single_check(self):
        """Run a single monitoring check"""
        self.logger.info("🔍 Running single monitoring check...")
        
        last_products = self.load_last_products()
        current_products = self.scrape_current_products()
        
        if not current_products:
            self.logger.error("❌ Failed to scrape products")
            return
        
        # Find new products
        current_keys = {f"{p['name']}_{p['price']}" for p in current_products}
        new_products = [p for p in current_products if f"{p['name']}_{p['price']}" not in last_products]
        
        # Check watchlist
        matched_products = self.check_watchlist(current_products)
        
        self.logger.info(f"📊 Current scan: {len(current_products)} total, {len(new_products)} new, {len(matched_products)} matches")
        
        if new_products or matched_products:
            self.send_email_notification(new_products, matched_products)
            self.save_last_products(current_products)
            self.save_monitoring_report(current_products, new_products, matched_products)
        else:
            self.logger.info("✅ No new products or watchlist matches")

if __name__ == "__main__":
    import sys
    
    monitor = HermesMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--single":
        monitor.run_single_check()
    else:
        monitor.monitor_loop()