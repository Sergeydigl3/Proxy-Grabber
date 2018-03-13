# -*- coding: utf8 -*-
import time
import requests
import random
from multiprocessing import Pool
from bs4 import BeautifulSoup


class ProxyGrabber:
    def __init__(self):
        self.user_ip = self.get_ip()
        try:
            self.useragents = open('./data/user-agent.list').read().split('\n')
        except FileNotFoundError:
            print('No useragents file')

        self.proxy_list = []
        self.checked_proxies = []

    def get_useragent(self):
        return random.choice(self.useragents)

    def get_proxy_list(self):
        return self.proxy_list

    def get_checked_proxies(self):
        return self.checked_proxies

    def get_proxy(self):
        return random.choice(self.check_proxies)

    def get_ip(self, proxies={}):
        return requests.get(url="http://httpbin.org/ip", proxies=proxies).text.split('"')[3]

    def load_proxies(self, filename='./data/proxy-list.txt'):
        file = open(filename, 'r')
        proxies = file.readlines()
        file.close()
        for proxy in proxies:
            self.proxy_list.append(proxy.rstrip())

    def save_proxies(self, proxies, filename='./data/proxy-list.txt'):
        file = open(filename, 'w')
        for proxy in proxies:
            file.write(proxy[7:] + '\n')
        file.close()

    def proxy_check(self, proxy):
        proxy = 'http://' + proxy
        try:
            result = requests.get('http://httpbin.org/ip', proxies={'http': proxy}, timeout=2.5)
            if result.status_code == 200:
                try:
                    if result.text.count('.') >=3 and result.text.split('"')[3] != self.user_ip:
                        return proxy
                except IndexError:
                    return False
            else:
                return False
        except requests.exceptions.ConnectionError:
            return False
        except requests.exceptions.ReadTimeout:
            return False
        except requests.exceptions.ChunkedEncodingError:
            return False

    def generate_proxy_list(self):
        proxy_list = []
        proxy_list += self._get_ipadress_proxy()
        proxy_list += self._get_proxyscale_proxy()
        proxy_list += self._get_freeproxylist_proxy()
        proxy_list += self._get_clarketm_list()
        # Leave only unique values
        proxy_list = list(set(proxy_list))
        self.proxy_list += proxy_list

    def check_proxies(self):
        with Pool(20) as p:
            proxy_list = p.map(self.proxy_check, self.proxy_list)
        checked_proxy_list = []

        for elem in proxy_list:
            if elem:
                checked_proxy_list.append(elem)

        self.checked_proxies = checked_proxy_list

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
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        result = soup.find('table',
                           id='proxylisttable').find('tbody').find_all('tr')
        proxy_list = []
        for elem in result:
            elem = str(elem)[8:-10].split('</td')
            if elem[4][5:] != 'transparent':
                proxy = elem[0] + ':' + elem[1][5:]
                proxy_list.append(proxy)
        return proxy_list


    def _get_clarketm_list(self):
        response = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt')
        proxies = response.text.split('\n')
        proxy_list = []
        for i in range(4, len(proxies) - 2):
            proxy_list.append(proxies[i].split(' ')[0])

        return proxy_list
