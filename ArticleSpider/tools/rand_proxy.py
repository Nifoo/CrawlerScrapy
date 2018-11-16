import requests
import time
import random


class RandProxy(object):
    agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
    headers = {"User-Agent": agent}
    proxy_list = []
    last_update_time = 0

    @classmethod
    def get_proxy(cls):
        if time.time() - cls.last_update_time > 600:
            content = requests.get('https://proxy.l337.tech/txt', headers=cls.headers, verify=False).content.strip()
            cls.proxy_list = content.split("\n")
        return random.choice(cls.proxy_list)


if __name__ == '__main__':
    print(RandProxy().get_proxy())
