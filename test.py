import datetime
import json
import logging
import time
import random
import traceback

import proxy
import pandas as pd
from selenium.webdriver.common.by import By

from send_email import send_email
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',
    datefmt='%Y-%m-%d %A %H:%M:%S',
    filename='test.log',
)




class ProductMonitorWithProxy:
    def __init__(self, url, subscribed_products=None, check_interval=5):
        self.url = url
        self.proxy = '127.0.0.1:7890'
        # self.proxy = 'http://LhXyjBvqWm24:0l5HtCXjRvGG_country-fr_ttl-30m_session-FNRwciKPfoNa@superproxy.zenrows.com:1337'
        self.check_interval = check_interval
        self.subscribed_products = subscribed_products or []

    def get_proxy(self):
        return self.proxy.get_proxy().get('proxy')

    def loads_local_proxies(self):
        proxies = []
        with open('proxy_ips', 'r') as f:
            for proxy in f.readlines():
                proxies.append(proxy.replace('\n', ''))
        return proxies

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
            x_offset = random.randint(0, element.size['width'] - 20)
            y_offset = random.randint(0, element.size['height'] - 20)
            action.move_to_element_with_offset(element, x_offset, y_offset).click().perform()
            logging.info(f"random click on x:{x_offset}, y: {y_offset}")

    def start_monitoring(self):
        print(f'Start monitoring url: {self.url}')
        while True:
            options = uc.ChromeOptions()
            # options.add_argument('headless')
            # options.add_argument('--disable-gpu')
            options.add_argument(f'--proxy-server={self.proxy}')
            # options.proxy = webdriver_proxy
            driver = uc.Chrome(options=options)
            # driver = webdriver.Chrome()
            try:
                if isinstance(self.url, list):
                    for url in self.url:
                        driver.get(url)
                        result = []
                        self.simulate_user_activity(driver)

                        recipient_email = "buweiyuqi@gmail.com"
                        # self.notify()
                        self.random_sleep(self.check_interval, self.check_interval + 10)
            except Exception as e:
                # print(f"Error accessing site with proxy {proxy_ip}: {e}")
                traceback.print_exc()

            finally:
                driver.quit()
                # self.proxy.delete_proxy(proxy_ip)
                logging.info('Driver quit...')

    def get_all_products(self):
        print(f'Start collecting url: {self.urls}')
        options = uc.ChromeOptions()
        # options.add_argument('headless')
        # options.add_argument('--disable-gpu')
        options.add_argument(f'--proxy-server={proxy}')
        driver = uc.Chrome(path='chromedriver', options=options)
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H:%m")
        try:
            result = []
            for url in self.urls:
                driver.get(url)
                response = driver.find_element(By.TAG_NAME, 'pre').text
                response = json.loads(response)
                # self.simulate_user_activity(driver)
                result += response['products']['items']
                self.save_items_from_api(response['products']['items'], date)
                self.random_sleep(self.check_interval, self.check_interval + 10)
            print(f'Total number of products: {len(result)}')
        except Exception as e:
            print(f"Error accessing site with proxy {proxy_ip}: {e}")
            traceback.print_exc()

        finally:
            # driver.quit()
            # self.proxy.delete_proxy(proxy_ip) TMP
            logging.info('Driver quit...')

    def is_new_product_available(self, driver, recipient_email):
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

    def save_items_from_api(self, products, date):
        # with open("products_list.json", 'w+') as f:
        #     json.dump(products, f)
        # print('Products Saved!')

        df = pd.DataFrame(products)
        df['url'] = df['url'].apply(lambda x: 'https://www.hermes.com/hk/en' + x)
        print(f'save {len(products)} products')
        df.to_csv(f'products-{date}.csv', index=False, mode='a')

    def notify_subscriber(self, product_id, product_element):
        product_details = "..."  # Extract necessary product details

        try:
            send_email("Product Available!", f"Product {product_id} is available: {product_details}", recipient_email)
            print(f"Notification sent for product {product_id}")
        except Exception as e:
            print(f"Failed to send notification for {product_id}: {e}")



if __name__ == "__main__":
    # https://bck.hermes.com/products?locale=us_en&category=WOMEN&sort=relevance&offset=48&pagesize=48&available_online=false
    # https://www.hermes.com/hk/en/category/women/#|
    # url = 'https://www.hermes.com/hk/en/content/316346-lindy-hermes-bags/'
    urls = ['https://www.hermes.com/fr/fr/category/femme/carres-chales-et-echarpes/carres-et-accessoires-de-soie/']
    # https://bck.hermes.com/products?locale=hk_en&category=WOMENBAGSBAGSCLUTCHES&sort=relevance&pagesize=48&available_online=false
    url_basic = 'https://bck.hermes.com/products?locale=hk_en&category=WOMENBAGSBAGSCLUTCHES&sort=relevance&pagesize={pagesize}&available_online=false'
    # urls = [url_basic + f'&offset={48 * i}&pagesize=48' for i in range(5)]
    urls = [url_basic.replace('{pagesize}', '48') for i in range(5)]
    monitor = ProductMonitorWithProxy(urls, check_interval=10)
    # monitor.get_all_products()
    monitor.start_monitoring()