import json
import logging
import time
import random
import traceback
from pprint import pprint

import proxy
import requests

from selenium.webdriver.common.by import By

from send_email import send_email
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.action_chains import ActionChains

logging.basicConfig(
    level=logging.DEBUG,  # 定义输出到文件的log级别，
    format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
    datefmt='%Y-%m-%d %A %H:%M:%S',  # 时间
    filename='test.log',  # log文件名
)


class MerchandiseMonitorWithProxy:
    def __init__(self, url, subscribed_products=None, check_interval=60):
        self.url = url
        # self.proxies = proxies
        self.check_interval = check_interval
        self.proxy = proxy.MyProxy(host='http://127.0.0.1', port='5010')
        self.subscribed_products = subscribed_products or []

    def get_proxy(self):
        return self.proxy.get_proxy().get('proxy')

    def random_sleep(self, min_seconds, max_seconds):
        t = random.uniform(min_seconds, max_seconds)
        time.sleep(t)
        print(f'Time sleep for {t}')

    def simulate_user_activity(self, driver):
        # Random scrolling
        scroll_length = random.randint(100, 1000)
        driver.execute_script(f"window.scrollBy(0, {scroll_length})")

        # Random delays
        self.random_sleep(0.5, 3)

        # Random clicks (if needed, ensure it's on a safe area)
        if random.choice([True, False]):
            action = ActionChains(driver)
            element = driver.find_element(By.TAG_NAME, 'body')
            print(element.size)
            x_offset = random.randint(0, element.size['width'] - 10)
            y_offset = random.randint(0, element.size['height'] - 10)
            action.move_to_element_with_offset(element, x_offset, y_offset).click().perform()
            logging.info(f"random click on x:{x_offset}, y: {y_offset}")

    def start_monitoring(self):
        print(f'Start monitoring url: {self.url}')
        while True:
            proxy_ip = self.get_proxy()
            print(f'proxy ip: {proxy_ip}')
            webdriver_proxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': proxy_ip,
                'ftpProxy': proxy_ip,
                'sslProxy': proxy_ip,
                'noProxy': ''
            })

            options = webdriver.ChromeOptions()
            # options.add_argument('headless')
            # options.add_argument('--disable-gpu')
            options.proxy = webdriver_proxy
            driver = webdriver.Chrome(options=options)
            # driver = webdriver.Chrome()

            try:
                print(f'Getting {self.url}')
                driver.get(self.url)
                self.simulate_user_activity(driver)

                recipient_email = "weiyuqi723@126.com"  # Replace with the recipient's email address

                # ... Inside your monitoring loop
                # if self.is_new_merchandise_available(driver, recipient_email):
                #     print("New merchandise available and email notification sent.")
                pprint(self.get_all_items(driver))

                self.random_sleep(self.check_interval, self.check_interval + 10)
            except Exception as e:
                print(f"Error accessing site with proxy {proxy_ip}: {e}")
                traceback.print_exc()

            finally:
                driver.quit()
                self.proxy.delete_proxy(proxy_ip)
                logging.info('Driver quit...')
                # self.random_sleep(self.check_interval, self.check_interval + 10)
            # driver.get(self.url)
            # self.simulate_user_activity(driver)
            #
            # recipient_email = "weiyuqi723@126.com"  # Replace with the recipient's email address
            #
            # # ... Inside your monitoring loop
            # if self.is_new_merchandise_available(driver, recipient_email):
            #     logging.info("New merchandise available and email notification sent.")
            #
            # self.random_sleep(self.check_interval, self.check_interval + 10)

    def is_new_merchandise_available(self, driver, recipient_email):
        try:
            element = driver.find_element(By.ID, 'new-merchandise-button')
            if element.is_displayed():
                logging.info(f"new product updated! {element}")
                send_email("New Merchandise Alert", "New merchandise is now available on the site!", recipient_email)
                logging.info(f'email send')
                return True
        except:
            return False

    def get_all_items(self, driver):
        # Find all product elements on the page
        product_elements = driver.find_elements(By.CLASS_NAME, "product-grid-list-item")

        products = []
        for element in product_elements:
            product_id = element.get_attribute('id').replace('grid-product-', '')
            product_info = {
                'product_id': product_id,
                'html': element.get_attribute('outerHTML'),
                'href': element.get_attribute('href')
            }
            products.append(product_info)
            # if product_id in self.subscribed_products:
            #     self.notify_subscriber(product_id, element)
        if products:
            with open('result.json', 'a+') as f:
                json.dump(products, f)

        return products

    def notify_subscriber(self, product_id, product_element):
        product_details = "..."  # Extract necessary product details
        try:
            send_email("Product Available!", f"Product {product_id} is available: {product_details}", recipient_email)
            print(f"Notification sent for product {product_id}")
        except Exception as e:
            print(f"Failed to send notification for {product_id}: {e}")


if __name__ == "__main__":
    # https://bck.hermes.com/products?locale=us_en&category=WOMEN&sort=relevance&offset=48&pagesize=48&available_online=false
    url = 'https://www.hermes.com/hk/en/category/women/#|'
    # url = 'https://bck.hermes.com/products?locale=hk_en&category=WOMEN&sort=relevance&available_online=false'
    monitor = MerchandiseMonitorWithProxy(url)
    monitor.start_monitoring()
