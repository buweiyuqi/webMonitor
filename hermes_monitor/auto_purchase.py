#!/usr/bin/env python3
"""
Hermès 自动购买模块
当检测到匹配的商品时，自动登录账号并尝试下单
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


class AutoPurchase:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.purchase_config = config.get("purchase", {})
        self.enabled = self.purchase_config.get("enabled", False)
        self.login_credentials = self.purchase_config.get("login_credentials", {})
        self.purchase_settings = self.purchase_config.get("purchase_settings", {})
        
        # 创建截图目录
        self.screenshot_dir = config.get("storage", {}).get("screenshot_dir", "result/screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
    def setup_driver(self, headless=False):
        """设置Chrome驱动用于购买流程"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        # 禁用图片加载以提高速度
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"驱动设置失败: {e}")
            return None
    
    def take_screenshot(self, driver, name):
        """截图保存"""
        if not self.purchase_settings.get("take_screenshots", True):
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        try:
            driver.save_screenshot(filepath)
            logger.info(f"截图已保存: {filepath}")
        except Exception as e:
            logger.warning(f"截图失败: {e}")
    
    def login(self, driver) -> bool:
        """执行登录流程"""
        try:
            logger.info("开始登录流程...")
            
            # 访问登录页面
            login_url = "https://www.hermes.com/hk/en/login"
            driver.get(login_url)
            
            # 等待页面加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.take_screenshot(driver, "login_page")
            
            # 查找并填写邮箱
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "j_username"))
            )
            email_field.clear()
            email_field.send_keys(self.login_credentials.get("email", ""))
            
            # 填写密码
            password_field = driver.find_element(By.NAME, "j_password")
            password_field.clear()
            password_field.send_keys(self.login_credentials.get("password", ""))
            
            # 点击登录按钮
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # 等待登录完成
            try:
                WebDriverWait(driver, 15).until(
                    EC.any_of(
                        EC.url_contains("account"),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".account-dashboard"))
                    )
                )
                logger.info("登录成功")
                self.take_screenshot(driver, "login_success")
                return True
                
            except TimeoutException:
                logger.error("登录超时或失败")
                self.take_screenshot(driver, "login_failed")
                return False
                
        except Exception as e:
            logger.error(f"登录过程中发生错误: {e}")
            self.take_screenshot(driver, "login_error")
            return False
    
    def navigate_to_product(self, driver, product_url: str) -> bool:
        """导航到商品页面"""
        try:
            logger.info(f"访问商品页面: {product_url}")
            driver.get(product_url)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.take_screenshot(driver, "product_page")
            return True
            
        except Exception as e:
            logger.error(f"访问商品页面失败: {e}")
            return False
    
    def add_to_bag(self, driver) -> bool:
        """添加到购物车"""
        try:
            logger.info("尝试添加到购物车...")
            
            # 查找添加到购物车按钮
            add_to_bag_selectors = [
                "button[data-add-to-bag]",
                "button[data-testid='add-to-bag']",
                "button[data-action='add-to-cart']",
                ".add-to-cart-button",
                "button:contains('Add to bag')",
                "button[aria-label*='Add to bag']"
            ]
            
            add_button = None
            for selector in add_to_bag_selectors:
                try:
                    if ":contains" in selector:
                        # 使用XPath处理包含文本的选择器
                        add_button = driver.find_element(By.XPATH, f"//button[contains(text(), 'Add to bag')]")
                    else:
                        add_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if add_button and add_button.is_displayed():
                        break
                except:
                    continue
            
            if not add_button:
                logger.error("未找到添加到购物车按钮")
                return False
            
            # 滚动到按钮位置
            driver.execute_script("arguments[0].scrollIntoView(true);", add_button)
            time.sleep(1)
            
            # 点击添加到购物车
            driver.execute_script("arguments[0].click();", add_button)
            
            # 等待确认
            try:
                WebDriverWait(driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".bag-item")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".mini-bag")),
                        EC.text_to_be_present_in_element((By.CSS_SELECTOR, "body"), "Added to bag")
                    )
                )
                logger.info("成功添加到购物车")
                self.take_screenshot(driver, "add_to_bag_success")
                return True
                
            except TimeoutException:
                logger.warning("添加到购物车后未收到确认")
                self.take_screenshot(driver, "add_to_bag_timeout")
                return False
                
        except Exception as e:
            logger.error(f"添加到购物车失败: {e}")
            self.take_screenshot(driver, "add_to_bag_error")
            return False
    
    def proceed_to_checkout(self, driver) -> bool:
        """前往结账"""
        try:
            logger.info("前往结账...")
            
            # 访问购物车页面
            bag_url = "https://www.hermes.com/hk/en/bag"
            driver.get(bag_url)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.take_screenshot(driver, "bag_page")
            
            # 查找结账按钮
            checkout_selectors = [
                "button[data-proceed-to-checkout]",
                "a[href*='checkout']",
                ".checkout-button",
                "button:contains('Proceed to checkout')"
            ]
            
            checkout_button = None
            for selector in checkout_selectors:
                try:
                    if ":contains" in selector:
                        checkout_button = driver.find_element(By.XPATH, f"//button[contains(text(), 'Proceed to checkout')]")
                    else:
                        checkout_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if checkout_button and checkout_button.is_displayed():
                        break
                except:
                    continue
            
            if not checkout_button:
                logger.error("未找到结账按钮")
                return False
            
            checkout_button.click()
            
            # 等待结账页面加载
            WebDriverWait(driver, 15).until(
                EC.url_contains("checkout")
            )
            
            logger.info("成功进入结账流程")
            self.take_screenshot(driver, "checkout_page")
            return True
            
        except Exception as e:
            logger.error(f"前往结账失败: {e}")
            self.take_screenshot(driver, "checkout_error")
            return False
    
    def attempt_purchase(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """尝试购买指定商品"""
        if not self.enabled:
            return {"success": False, "error": "自动购买未启用"}
        
        driver = None
        result = {
            "success": False,
            "product": product,
            "start_time": datetime.now().isoformat(),
            "error": None,
            "screenshots": []
        }
        
        try:
            # 检查价格限制
            price = int(product.get('price', '0').replace(',', '')) if str(product.get('price', '0')).isdigit() else 0
            max_price = self.purchase_settings.get("max_price", 100000)
            
            if price > max_price:
                result["error"] = f"价格 {price} 超过最大购买价格 {max_price}"
                return result
            
            # 设置驱动
            driver = self.setup_driver(headless=False)  # 购买流程需要可见浏览器
            if not driver:
                result["error"] = "无法初始化浏览器驱动"
                return result
            
            # 执行购买流程
            logger.info(f"开始购买流程: {product.get('name', 'Unknown Product')}")
            
            # 1. 登录
            if not self.login(driver):
                result["error"] = "登录失败"
                return result
            
            # 2. 访问商品页面
            if not self.navigate_to_product(driver, product.get('product_url', '')):
                result["error"] = "无法访问商品页面"
                return result
            
            # 3. 添加到购物车
            if not self.add_to_bag(driver):
                result["error"] = "添加到购物车失败"
                return result
            
            # 4. 前往结账
            if not self.proceed_to_checkout(driver):
                result["error"] = "前往结账失败"
                return result
            
            # 如果到达这里，说明购买流程成功启动
            result["success"] = True
            logger.info("购买流程已成功启动")
            
        except Exception as e:
            logger.error(f"购买过程中发生错误: {e}")
            result["error"] = str(e)
            
        finally:
            if driver:
                self.take_screenshot(driver, "purchase_final")
                driver.quit()
            
            result["end_time"] = datetime.now().isoformat()
            self.save_purchase_record(result)
        
        return result
    
    def save_purchase_record(self, result: Dict[str, Any]):
        """保存购买记录"""
        try:
            history_file = self.config.get("storage", {}).get("purchase_history_file", "result/purchase_history.json")
            
            # 读取现有记录
            history = []
            if os.path.exists(history_file):
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                except:
                    history = []
            
            # 添加新记录
            history.append(result)
            
            # 保存记录
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            
            logger.info(f"购买记录已保存: {len(history)} 条记录")
            
        except Exception as e:
            logger.error(f"保存购买记录失败: {e}")
    
    def is_purchase_enabled(self) -> bool:
        """检查是否启用了自动购买"""
        return self.enabled