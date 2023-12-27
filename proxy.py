import requests
class MyProxy:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_proxy(self):
        return requests.get(f"{self.host}:{self.port}/get/").json()

    def delete_proxy(self, proxy):
        requests.get(f"{self.host}:{self.port}/delete/?proxy={proxy}")