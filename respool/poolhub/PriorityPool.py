import redis
import configparser
import os
import logging
import random

from singleton import singleton
from config import config
from time import time,sleep


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt = '[%Y-%m-%d  %H:%M:%S]'
                    )


resource_path = "./resource.txt"

@singleton
class PriorityPool(object):
    def __init__(self, resource_path=resource_path, rhost=None, rport=None, rusername=None, rpassword=None, rdb=None, 
            connect_timeout=None, reload_resource=None):
        
        self.resource_path = resource_path
        self.rhost = rhost or config.REDIS_HOST
        self.rport = rport or config.REDIS_PORT
        self.rdb = rdb or config.REDIS_DB
        self.rusername = rusername or config.REDIS_USERNAME
        self.rpassword = rpassword or config.REDIS_PASSWORD
        self.reload_resource = reload_resource or config.RELOAD_RESOURCE_PRIORITY

        self.new_redis_client()
        self._load_resource_and_create_key()


    def new_redis_client(self):
        self.rclient = redis.StrictRedis(host=self.rhost, port=self.rport,db=self.rdb, decode_responses=True)


    def _load_resource_and_create_key(self):
        self.key_name = "priority_respool_main"   # sortedset
        self.total_weight = 0
        if not self.reload_resource and self.key_name in self.rclient.keys():
            for member in self.rclient.zscan_iter(self.key_name):    # 重新获取所有资源的总权重
                self.total_weight += member[1]
            return 
        with open(self.resource_path, mode="r") as f:
            for line in f:
                member = line.strip()
                self.rclient.zadd(self.key_name, {str(member):config.PRIORITY_INIT_SCORE})
                self.total_weight += config.PRIORITY_INIT_SCORE
        logging.info("load {} objects to priority pool {}".format(self.rclient.zcard(self.key_name), self.key_name))


    def grab_one(self):
        self.new_redis_client()
        rand_num = random.uniform(-0.01, self.total_weight)
        iter_weight = 0
        for member in self.rclient.zscan_iter(self.key_name):
            iter_weight += member[1]
            if iter_weight >= rand_num:
                return {"res":member[0], "score":member[1]}


    def dec_weight(self, res):
        self.new_redis_client()
        old_score = self.rclient.zscore(self.key_name, res)
        if not old_score:
            return {"msg":"fail"} 
        self.rclient.zadd(self.key_name, {res:old_score-1})
        self.total_weight -= 1
        return {"msg":"success"}

    def pool_size(self):
        self.new_redis_client()
        return {"pool_size": self.rclient.zcard(self.key_name)}

    def clear_pool(self):
        self.new_redis_client()
        self.rclient.delete(self.key_name)
