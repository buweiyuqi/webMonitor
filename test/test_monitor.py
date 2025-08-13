#!/usr/bin/env python3
"""
Hermès Test Wrapper
Uses the existing hermes_monitor.py functionality with test server configuration
"""

import sys
import os
import json
from datetime import datetime

# Import the main monitoring class
sys.path.append(os.path.dirname(__file__) + '/..')

try:
    from hermes_monitor import HermesMonitor
    print("✅ Successfully imported HermesMonitor from hermes_monitor.py")
except ImportError as e:
    print(f"❌ Error importing HermesMonitor: {e}")
    print("Make sure hermes_monitor.py is in the parent directory")
    exit(1)

class TestHermesWrapper:
    def __init__(self):
        self.test_config_file = "test_config.json"
        self.original_config_file = "config.json"
        
    def run_test(self):
        """Run test with test configuration"""
        print("🧪 Starting test with test configuration...")
        print(f"📄 Using config: {self.test_config_file}")
        
        # Create test config if it doesn't exist
        self.ensure_test_config()
        
        # Create test monitor with test config
        monitor = HermesMonitor(self.test_config_file)
        
        # Override scrape function for test server
        def scrape_test_products():
            """Override scraping to use test server"""
            import requests
            try:
                response = requests.get("http://localhost:5001/api/products", timeout=10)
                response.raise_for_status()
                data = response.json()
                return data.get('products', [])
            except Exception as e:
                monitor.logger.error(f"Test server error: {e}")
                return []
        
        # Replace the scraping method
        monitor.scrape_current_products = scrape_test_products
        
        # Override the result directory
        monitor.result_dir = "../result"
        monitor.last_products_file = "../result/test_last_products.json"
        monitor.config["storage"]["log_file"] = "../result/test_monitor.log"
        
        print("✅ Test monitor configured successfully")
        
        if len(sys.argv) > 1 and sys.argv[1] == "--loop":
            print("🔍 Starting continuous test monitoring...")
            monitor.monitor_loop()
        else:
            print("🔍 Running single test check...")
            monitor.run_single_check()
    
    def ensure_test_config(self):
        """Ensure test config exists, read from existing config if available"""
        if os.path.exists(self.test_config_file):
            try:
                with open(self.test_config_file, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
                print(f"📄 Using existing test config: {self.test_config_file}")
                return
            except json.JSONDecodeError:
                print(f"⚠️  Existing test config is invalid, recreating...")
        
        # Load base config if exists
        base_config = {}
        if os.path.exists(self.original_config_file):
            try:
                with open(self.original_config_file, 'r', encoding='utf-8') as f:
                    base_config = json.load(f)
                print(f"📄 Loaded base config from: {self.original_config_file}")
            except json.JSONDecodeError:
                print(f"⚠️  Base config invalid, using defaults...")
        
        # Create test config with server-specific overrides
        test_config = base_config.copy()
        test_config.update({
            "monitoring": {
                "check_interval_minutes": 1,
                "urls": ["http://localhost:5001/api/products"]
            },
            "email": {
                "smtp_server": test_config.get("email", {}).get("smtp_server", "smtp.163.com"),
                "smtp_port": test_config.get("email", {}).get("smtp_port", 465),
                "sender_email": test_config.get("email", {}).get("sender_email", "inform723@163.com"),
                "sender_password": "test_password",  # Override for testing
                "recipient_emails": test_config.get("email", {}).get("recipient_emails", ["weiyuqi723@126.com"]),
                "subject_prefix": "[TEST监控]"
            },
            "storage": {
                "last_products_file": "result/test_last_products.json",
                "log_file": "result/test_monitor.log"
            }
        })
        
        # Ensure watchlist exists
        if "watchlist" not in test_config:
            test_config["watchlist"] = {
                "products": [
                    {"name_contains": "Birkin", "max_price": 100000, "min_price": 80000},
                    {"name_contains": "Kelly", "max_price": 90000, "min_price": 70000},
                    {"name_contains": "Limited", "max_price": 200000, "min_price": 100000},
                    {"name_contains": "Special", "max_price": 100000, "min_price": 50000}
                ]
            }
        
        with open(self.test_config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Test config updated: {self.test_config_file}")

if __name__ == "__main__":
    wrapper = TestHermesWrapper()
    
    print("🧪 Hermès Test Wrapper")
    print("=" * 50)
    print("This uses the existing hermes_monitor.py with test server")
    print("=" * 50)
    
    try:
        wrapper.run_test()
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure test server is running: cd test && python3 test_server.py")