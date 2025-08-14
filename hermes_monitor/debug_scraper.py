#!/usr/bin/env python3
"""
调试版本 - 用于诊断产品抓取问题
"""

import json
import time
import os
from datetime import datetime
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

class DebugScraper:
    def __init__(self):
        self.result_dir = "../result"
        os.makedirs(self.result_dir, exist_ok=True)
        
        # 设置详细日志
        logger.add("../result/debug.log", level="DEBUG")
        self.logger = logger
    
    def setup_driver_debug(self, headless=False):
        """设置调试模式的Chrome驱动"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        # 添加调试选项
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 禁用图片加载以提高速度
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            self.logger.error(f"驱动设置失败: {e}")
            return None
    
    def debug_page_source(self, url):
        """调试页面源代码"""
        driver = self.setup_driver_debug(headless=False)  # 使用可见模式调试
        if not driver:
            return None
        
        try:
            self.logger.info(f"访问页面: {url}")
            driver.get(url)
            
            # 等待页面加载
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 等待额外时间让JS加载
            time.sleep(5)
            
            # 保存页面源代码
            page_source = driver.page_source
            with open(f"{self.result_dir}/page_source_debug.html", "w", encoding="utf-8") as f:
                f.write(page_source)
            
            self.logger.info(f"页面源代码已保存到 {self.result_dir}/page_source_debug.html")
            
            # 截图
            driver.save_screenshot(f"{self.result_dir}/page_screenshot_debug.png")
            self.logger.info(f"页面截图已保存到 {self.result_dir}/page_screenshot_debug.png")
            
            # 分析页面结构
            self.logger.info("分析页面结构...")
            
            # 查找所有可能的商品容器
            possible_selectors = [
                '[data-testid="product-tile"]',
                '.product-item',
                '.product-card',
                'article',
                '.product-tile',
                '.item',
                '.grid-item',
                '.product'
            ]
            
            all_elements = []
            for selector in possible_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        self.logger.info(f"找到 {len(elements)} 个元素使用选择器: {selector}")
                        all_elements.extend(elements)
                except Exception as e:
                    self.logger.debug(f"选择器 {selector} 失败: {e}")
            
            # 调试商品提取
            products = []
            for element in all_elements[:10]:  # 只检查前10个
                try:
                    product = self.debug_extract_details(driver, element)
                    if product and product.get('name'):
                        products.append(product)
                        self.logger.info(f"找到商品: {product}")
                except Exception as e:
                    self.logger.debug(f"提取商品失败: {e}")
            
            self.logger.info(f"总共找到 {len(products)} 个商品")
            return products
            
        except Exception as e:
            self.logger.error(f"调试过程发生错误: {e}")
            return []
        finally:
            driver.quit()
    
    def debug_extract_details(self, driver, element):
        """调试版本的产品详情提取"""
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
            # 获取元素HTML用于调试
            element_html = element.get_attribute('outerHTML')[:200] + "..."
            self.logger.debug(f"处理元素: {element_html}")
            
            # 商品名称
            name_selectors = [
                '.product-name', '.product-title', 'h3', 'h2',
                '[data-testid="product-title"]', '.item-name',
                '.title', '.name', '.product-item-name',
                '.product__name', '.product-card__title'
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    name = name_elem.text.strip()
                    if name and len(name) > 3:
                        product['name'] = name
                        self.logger.debug(f"使用选择器 {selector} 找到名称: {name}")
                        break
                except:
                    continue
            
            # 价格
            price_selectors = [
                '.price', '.product-price', '[data-price]',
                '.current-price', '.amount', '.price-value',
                '.product-price__value', '.price--current'
            ]
            
            for selector in price_selectors:
                try:
                    price_elem = element.find_element(By.CSS_SELECTOR, selector)
                    price_text = price_elem.text.strip()
                    if price_text:
                        price_match = re.search(r'[\d,]+', price_text.replace(',', ''))
                        if price_match:
                            product['price'] = price_match.group()
                            self.logger.debug(f"使用选择器 {selector} 找到价格: {price_match.group()}")
                            break
                except:
                    continue
            
            # 图片URL
            try:
                img_elem = element.find_element(By.CSS_SELECTOR, 'img')
                img_src = img_elem.get_attribute('src') or img_elem.get_attribute('data-src')
                if img_src:
                    if img_src.startswith('//'):
                        img_src = 'https:' + img_src
                    elif img_src.startswith('/'):
                        img_src = "https://www.hermes.com" + img_src
                    product['image_url'] = img_src
                    self.logger.debug(f"找到图片: {img_src}")
            except:
                pass
            
            # 产品URL
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, 'a[href*="/product/"]')
                href = link_elem.get_attribute('href')
                if href:
                    product['product_url'] = href if href.startswith('http') else "https://www.hermes.com" + href
                    
                    # 提取SKU
                    sku_match = re.search(r'H[A-Z0-9]+', href)
                    if sku_match:
                        product['sku'] = sku_match.group()
                    self.logger.debug(f"找到产品链接: {product['product_url']}")
            except:
                pass
            
        except Exception as e:
            self.logger.debug(f"提取详情错误: {e}")
        
        return product if product['name'] else None
    
    def test_connection(self, url):
        """测试网站连接"""
        driver = self.setup_driver_debug(headless=True)
        if not driver:
            return False
        
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            title = driver.title
            self.logger.info(f"页面标题: {title}")
            
            # 检查是否需要验证码
            if "robot" in driver.page_source.lower() or "captcha" in driver.page_source.lower():
                self.logger.warning("检测到验证码或机器人检查")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"连接测试失败: {e}")
            return False
        finally:
            driver.quit()

if __name__ == "__main__":
    scraper = DebugScraper()
    
    # 测试连接
    test_url = "https://www.hermes.com/hk/en/category/women/bags-and-small-leather-goods/bags-and-clutches/"
    
    print("🔍 开始调试产品抓取...")
    
    # 测试连接
    print("测试网站连接...")
    if scraper.test_connection(test_url):
        print("✅ 网站连接正常")
    else:
        print("❌ 网站连接异常")
    
    # 调试抓取
    print("开始调试抓取...")
    products = scraper.debug_page_source(test_url)
    
    if products:
        print(f"✅ 成功抓取到 {len(products)} 个产品")
        for i, product in enumerate(products[:3], 1):
            print(f"{i}. {product['name']} - {product['price']}HKD")
    else:
        print("❌ 未能抓取到任何产品")
        print("请检查 debug.log 和页面源代码文件获取更多信息")