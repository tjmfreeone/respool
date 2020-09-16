import redis
import os
import logging
import random
import requests
from lxml import etree

from singleton import singleton

from config import config
from time import time,sleep


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt = '[%Y-%m-%d  %H:%M:%S]'
                    )



@singleton
class ProxyPool(object):
    def __init__(self, rhost=None, rport=None, rusername=None, rpassword=None, rdb=None, connect_timeout=None):

        self.rhost = rhost or config.REDIS_HOST
        self.rport = rport or config.REDIS_PORT
        self.rdb = rdb or config.REDIS_DB
        self.rusername = rusername or config.REDIS_USERNAME
        self.rpassword = rpassword or config.REDIS_PASSWORD

        self.proxy_source = {
                "kuaidaili": kuaidaili(),
                }

        self.new_redis_client()
        self.supply()


    def new_redis_client(self):
        self.rclient = redis.StrictRedis(host=self.rhost, port=self.rport,db=self.rdb, decode_responses=True)


    def supply(self):
        self.key_name = "proxy_respool_main"   # sortedset
        self.total_weight = 0
        if self.key_name in self.rclient.keys():
            for member in self.rclient.zscan_iter(self.key_name):    # 重新获取所有代理的总权重
                self.total_weight += member[1]
            return
        self.proxy_source[config.PROXY_SOURCE].keep_crawl_until_reach_capacity()
        for proxy in self.proxy_source[config.PROXY_SOURCE].proxy_list:
            self.rclient.zadd(self.key_name, {proxy:config.PROXY_INIT_SCORE})
            self.total_weight += config.PROXY_INIT_SCORE
        logging.info("load {} objects to proxy pool {}".format(self.rclient.zcard(self.key_name), self.key_name))


    def grab_one(self):
        self.new_redis_client()
        rand_num = random.uniform(-0.01, self.total_weight)
        iter_weight = 0
        for member in self.rclient.zscan_iter(self.key_name):
            iter_weight += member[1]
            if iter_weight >= rand_num:
                return {"ip":member[0].split(":")[0], 
                        "port":member[0].split(":")[1], 
                        "score":member[1]}


    def dec_weight(self, res):
        self.new_redis_client()
        old_score = self.rclient.zscore(self.key_name, res)
        if not old_score:
            return {"msg":"fail"} 
        self.rclient.zadd(self.key_name, {res:old_score-1})
        self.total_weight -= 1
        return {"msg":"success"}


    def clear_pool(self):
        self.new_redis_client()
        self.rclient.delete(self.key_name)


class kuaidaili():
    def __init__(self, crawl_retry=3):
        self.proxy_list = []
        self.crawl_retry = crawl_retry

    def crawl_single_page(self, page):
        have_try = 0
        while True:     # 抓取代理重试次数
            sleep(1)
            if have_try >= self.crawl_retry:
                logging.info("retry {} times, can not crawl any proxy.".format(have_try))
                break
            resp = requests.get("https://www.kuaidaili.com/free/inha/{}/".format(page))
            tree = etree.HTML(resp.text)
            tree = tree.xpath('//table//tbody//tr')
            for proxy_tree in tree:
                ip = proxy_tree.xpath('.//td[@data-title="IP"]/text()')[0]
                port = proxy_tree.xpath('.//td[@data-title="PORT"]/text()')[0]
                self.proxy_list.append(ip+":"+port) 
            break
                
    def keep_crawl_until_reach_capacity(self):
        page = 1
        while True:
            if len(self.proxy_list) >= config.CAPACITY:
                logging.info("proxy pool supply finished")
                break
            self.crawl_single_page(page)
            page += 1


