import redis
import configparser
import os
import logging
import random
from singleton import singleton

from time import time,sleep


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt = '[%Y-%m-%d  %H:%M:%S]'
                    )

cf = configparser.ConfigParser()
cf.read("./config.ini")

redis_cf = dict(cf.items('redis'))
pool_type_cf = dict(cf.items('pool-type'))
cooldown_cf = dict(cf.items('cooldown'))
init_score_cf = dict(cf.items('init-score'))

resource_path = "./resource.txt"

@singleton
class PriorityPool(object):
    def __init__(self, resource_path=resource_path, rhost=None, rport=None, rusername=None, rpassword=None, rdb=None, connect_timeout=None):

        self.resource_path = resource_path
        self.rhost = rhost or redis_cf['host']
        self.rport = rport or redis_cf[ 'port']
        self.rdb = rdb or redis_cf[ 'db']
        self.rusername = rusername or redis_cf[ 'username']
        self.rpassword = rpassword or redis_cf[ 'password']

        self.new_redis_client()
        self._load_resource_and_create_key()


    def new_redis_client(self):
        self.rclient = redis.StrictRedis(host=self.rhost, port=self.rport,db=self.rdb, decode_responses=True)


    def _load_resource_and_create_key(self):
        self.key_name = "priority_respool_main"   # sortedset
        self.total_weight = 0
        with open(self.resource_path, mode="r") as f:
            for line in f:
                member = line.strip()
                self.rclient.zadd(self.key_name, {str(member):init_score_cf["score"]})
                self.total_weight += eval(init_score_cf["score"])
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
