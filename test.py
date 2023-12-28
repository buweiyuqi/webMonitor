import json
import logging
import time
import random
import traceback

import proxy

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
    def __init__(self, urls, subscribed_products=None, check_interval=5):
        self.urls = urls
        # self.proxies = proxies
        self.proxies = self.loads_local_proxies()
        self.check_interval = check_interval
        self.proxy = proxy.MyProxy(host='http://127.0.0.1', port='5010')
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
            x_offset = random.randint(0, element.size['width'] - 10)
            y_offset = random.randint(0, element.size['height'] - 10)
            action.move_to_element_with_offset(element, x_offset, y_offset).click().perform()
            logging.info(f"random click on x:{x_offset}, y: {y_offset}")

    def start_monitoring(self):
        print(f'Start monitoring url: {self.urls}')
        while True:
            proxy_ip = random.choice(self.proxies)
            print(f'proxy ip: {proxy_ip}')
            # webdriver_proxy = Proxy({
            #     'proxyType': ProxyType.MANUAL,
            #     'httpProxy': proxy_ip,
            #     'ftpProxy': proxy_ip,
            #     'sslProxy': proxy_ip,
            #     'noProxy': ''
            # })
            # webdriver_proxy = Proxy({
            #     'proxyType': ProxyType.MANUAL,
            #     'httpProxy': '127.0.0.1:7890',
            #     'ftpProxy': '127.0.0.1:7890',
            #     'sslProxy': '127.0.0.1:7890',
            #     'noProxy': ''
            # })

            options = uc.ChromeOptions()
            # options.add_argument('headless')
            # options.add_argument('--disable-gpu')
            options.add_argument(f'--proxy-server={proxy_ip}')
            # options.proxy = webdriver_proxy
            driver = uc.Chrome(options=options)
            # driver = webdriver.Chrome()

            try:
                driver.get('https://nowsecure.nl')
                pre_url = 'https://www.hermes.com/hk/en/category/women/#|'
                driver.get(pre_url)
                str_cookies = """
                {
                    "_gcl_au": "1.1.1999447864.1703668752",
                    "_gid": "GA1.2.2031282288.1703668752",
                    "_gcl_aw": "GCL.1703668755.CjwKCAiAs6-sBhBmEiwA1Nl8swygJIazS7n1L-12P8yEKSQhImbSQxczYjCC0KBvP5fxTVLhHBphWRoCDlIQAvD_BwE",
                    "_gcl_dc": "GCL.1703668755.CjwKCAiAs6-sBhBmEiwA1Nl8swygJIazS7n1L-12P8yEKSQhImbSQxczYjCC0KBvP5fxTVLhHBphWRoCDlIQAvD_BwE",
                    "GeoFilteringBanner": "1",
                    "_gac_UA-64545050-1": "1.1703668775.CjwKCAiAs6-sBhBmEiwA1Nl8swygJIazS7n1L-12P8yEKSQhImbSQxczYjCC0KBvP5fxTVLhHBphWRoCDlIQAvD_BwE",
                    "x-xsrf-token": "01ab0375-fc16-4f84-90a9-383d55b576fa",
                    "correlation_id": "4640tun2r1cy84behp407l1eiz5sct87o9vm2i06fzen2kbtdww7mxxydtqr3yc5",
                    "rskxRunCookie": "0",
                    "rCookie": "e7h4e6uv78p9f6zw9zix08lqnkelts",
                    "_fbp": "fb.1.1703668874990.1342944327",
                    "lastRskxRun": "1703668991059",
                    "_uetsid": "ff771a60a49811ee9d737b956ee4f0e8",
                    "_uetvid": "ff775690a49811eea009c1d73b608275",
                    "_cs_c": "1",
                    "_cs_id": "704df16b-a9d5-ac0a-98b3-c5e44076861e.1703684995.1.1703684995.1703684995.1.1737848995989",
                    "ECOM_SESS": "5fe9w16n0v0yksii8d3nqz6zif",
                    "_cs_mk": "0.10211864199946152_1703734631765",
                    "_ga": "GA1.2.1494663094.1703668752",
                    "_ga_Y862HCHCQ7": "GS1.1.1703734632.4.0.1703734633.0.0.0",
                    "datadome": "o4LZLp0t6Baos7wfeMc2Br3_8GeZVWYq7c2Nny93Do~MDKKN7A~RvBhY0K23PsPHr_rsG2cnnb1BokfBl_Z82gefopSkQfnJTFXSUnrugq_ojEX751QimejpciVxyHj2"
                }
                """
                cookies = json.loads(str_cookies)
                driver.delete_all_cookies()
                for key, value in cookies.items():
                    driver.add_cookie({"name": key, "value": value})
                # driver.add_cookies(cookies)
                driver.refresh()
                for url in self.urls:
                    result = driver.get(url)
                    self.simulate_user_activity(driver)

                    recipient_email = "weiyuqi723@126.com"  # Replace with the recipient's email address

                    # ... Inside your monitoring loop
                    # if self.is_new_merchandise_available(driver, recipient_email):
                    #     print("New merchandise available and email notification sent.")
                    # self.get_all_items(driver)
                    self.save_items_from_api(result['products'])

                    self.random_sleep(self.check_interval, self.check_interval + 10)
            except Exception as e:
                print(f"Error accessing site with proxy {proxy_ip}: {e}")
                traceback.print_exc()

            finally:
                driver.quit()
                self.proxy.delete_proxy(proxy_ip)
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

    def save_items_from_api(self, products):
        with open("products_list.json", 'w+') as f:
            json.dump(products, f)
        print('Products Saved!')

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

    url_basic = 'https://bck.hermes.com/products?locale=hk_en&category=WOMEN&sort=relevance&available_online=false'
    urls = [url_basic + f'&offset={500 * i}&pagesize=500' for i in range(5)]
    monitor = ProductMonitorWithProxy(urls, check_interval=10)
    monitor.start_monitoring()


#CRUo6xiI89nvkfXn4tH9PJuBFYyJ