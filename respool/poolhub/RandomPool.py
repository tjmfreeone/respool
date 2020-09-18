import redis
import os
import logging
import random
from singleton import singleton  
from time import time,sleep
from config import config

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt = '[%Y-%m-%d  %H:%M:%S]'
                    )

resource_path = "./resource.txt"

@singleton
class RandomPool(object):
    def __init__(self, resource_path=resource_path, rhost=None, rport=None, rusername=None, rpassword=None, rdb=None, connect_timeout=None, 
                enable_cooldown=None, cooldown_time=None, refresh_interval=None, reload_resource=None):

        self.resource_path = resource_path
        self.rhost = rhost or config.REDIS_HOST
        self.rport = rport or config.REDIS_PORT
        self.rdb = rdb or config.REDIS_DB
        self.rusername = rusername or config.REDIS_USERNAME
        self.rpassword = rpassword or config.REDIS_PASSWORD

        self.enable_cooldown = enable_cooldown or config.COOLDOWN_ENABLE
        self.cooldown_time = cooldown_time or config.COOLDOWN_TIME
        self.refresh_interval = refresh_interval or config.REFRESH_INTERVAL
        self.reload_resource = reload_resource or config.RELOAD_RESOURCE_RANDOM

        self.new_redis_client()
        self._load_resource_and_create_key()


    def new_redis_client(self):
        self.rclient = redis.StrictRedis(host=self.rhost, port=self.rport, db=self.rdb, decode_responses=True)


    def _load_resource_and_create_key(self):
        self.key_name = "random_respool_main"    #set
        self.cooldown_pool_name = "random_cooldown_pool"  #set
        if not self.reload_resource:
            return 
        with open(self.resource_path, mode='r') as f:
            for line in f:
                member = line.strip()
                self.rclient.sadd(self.key_name, member)
        logging.info("load {} objects to random pool {}".format(self.rclient.scard(self.key_name), self.key_name))


    def grab_one(self):
        self.new_redis_client()
        if self.enable_cooldown and self.cooldown_time:
            member = self.rclient.spop(self.key_name)
            if member:
                new_member = {"res":member,"join_ts":int(time())}
                self.rclient.sadd(self.cooldown_pool_name, str(new_member))
            res = {"res":member}
        else:
            member = self.rclient.srandmember(self.key_name)
            res = {"res":member}
        return res

    def refresh_cooldown_pool(self):
        self.new_redis_client()
        while True:
            now = int(time())
            sleep(self.refresh_interval)
            for member in self.rclient.smembers(self.cooldown_pool_name):
                if now >= eval(member)["join_ts"] + self.cooldown_time:
                    self.rclient.srem(self.cooldown_pool_name, member)
                    self.rclient.sadd(self.key_name, eval(member)["res"])

    def pool_size(self):
        self.new_redis_client()
        return {"pool_size": self.rclient.scard(self.key_name)}

    def clear_pool(self):
        self.new_redis_client()
        self.rclient.delete(self.key_name)
        self.rclient.delete(self.cooldown_pool_name)

