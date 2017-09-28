# -*- coding: utf8 -*-
import time
import requests
import random
from multiprocessing import Pool
from bs4 import BeautifulSoup


class Proxy:
    def __init__(self, user_ip):
        self.user_ip = user_ip
        self.useragents = open('useragents.txt').read().split('\n')
        self.proxy_list = self.generate_proxy_list()

    def get_useragent(self):
        return random.choice(self.useragents)

    def get_proxy_list(self):
        return self.proxy_list

    def get_proxy(self):
        return random.choice(self.proxy_list)

    @staticmethod
    def proxy_check(proxy):
        proxy = 'http://' + proxy
        try:
            result = requests.get('http://ya.ru', proxies={'http': proxy}, timeout=2.5)
            if result.status_code == 200:
                return proxy
            else:
                return False
        except requests.exceptions.ConnectionError:
            return False
        except requests.exceptions.ReadTimeout:
            return False
        except requests.exceptions.ChunkedEncodingError:
            return False

    def anonymity_check(self, proxy):
        useragent = {'user-agent': self.get_useragent()}
        proxy = 'http://' + proxy
        target_url = 'https://whoer.net/ru'
        result = requests.get(target_url, proxies={'http': proxy}, headers=useragent)
        soup = BeautifulSoup(result.text, "lxml")
        pars_result = soup.find(class_='your-ip').text
        # The result is ip_address:port and we need ip part
        if ':' in pars_result:
            pars_result = pars_result[:pars_result.index(':')]
        if self.user_ip == pars_result:
            return False
        return True

    def generate_proxy_list(self):
        proxy_list = []
        proxy_list += self._get_ipadress_proxy()
        proxy_list += self._get_proxyscale_proxy()
        proxy_list += self._get_freeproxylist_proxy()
        # Leave only unique values
        proxy_list = list(set(proxy_list))

        with Pool(40) as p:
            proxy_list = p.map(self.proxy_check, proxy_list)
        checked_proxy_list = []

        for elem in proxy_list:
            if elem:
                checked_proxy_list.append(elem)

        return checked_proxy_list

    def _get_ipadress_proxy(self):
        target_url = 'https://www.ip-adress.com/proxy-list'
        result = requests.get(target_url)
        soup = BeautifulSoup(result.text, "lxml")
        pars_result = soup.find('tbody').find_all('tr')
        proxy_list = []
        for elem in pars_result:
            elem = elem.get_text().split()[:2]
            if elem[1] != 'transparent':
                proxy_list.append(elem[0])
        return proxy_list

    def _get_proxyscale_proxy(self):
        target_url_beginning_part = 'http://free.proxy-sale.com/?pg='
        target_url_ending_part = '&port[]=http&type[]=an&type[]=el'
        result = requests.get(target_url_beginning_part + target_url_ending_part)
        soup = BeautifulSoup(result.text, "lxml")
        pages_number = int(soup.find_all('a', class_='pag-bg')[-1].get_text())

        ip_list = []
        urls = self._generate_urls(pages_number,
                                   target_url_beginning_part, target_url_ending_part)

        with Pool(7) as p:
            map_result = p.map(self._parse, urls)

        for elem in map_result:
            ip_list += elem

        return ip_list

    def _generate_urls(self, pages_count, target_url_bp, target_url_ep):
        urls = []
        for i in range(pages_count):
            target_url = target_url_bp + str(i + 1) + target_url_ep
            urls.append(target_url)
        return urls

    def _parse(self, target_url):
        time.sleep(random.uniform(0.5, 2))
        result = requests.get(target_url)
        soup = BeautifulSoup(result.text, "lxml")
        ports = []
        ip_port = []
        for elem in soup.find('tbody').find_all('img'):
            if 'imgport' in elem.get('src'):
                ports.append(str(elem)[28:str(elem).index('"/>')])

        proxy_list = []
        for elem in soup.find('tbody').find_all('tr'):
            proxy_list.append(elem.get_text().split()[0])

        for i in range(len(ports)):
            ip_port.append(proxy_list[i] + ':' + ports[i])
        return ip_port

    def _get_freeproxylist_proxy(self):

        result = []
        result += self._get_proxy_list('https://us-proxy.org/')
        result += self._get_proxy_list('https://free-proxy-list.net/')
        return result

    def _get_proxy_list(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        result = soup.find('table',
                           id='proxylisttable').find('tbody').find_all('tr')
        proxy_list = []
        for elem in result:
            elem = str(elem)[8:-10].split('</td')
            if elem[4][5:] != 'transparent':
                proxy = elem[0] + ':' + elem[1][5:]
                proxy_list.append(proxy)
        return proxy_list
