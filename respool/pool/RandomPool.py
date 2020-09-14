import redis
import configparser
import os
import logging
import random

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

resource_path = "./resource.txt"

class RandomPool(object):
    def __init__(self, resource_path=resource_path, rhost=None, rport=None, rusername=None, rpassword=None, rdb=None, connect_timeout=None, 
                enable_cooldown=None, cooldown_time=None):

        self.resource_path = resource_path
        self.rhost = rhost or redis_cf['host']
        self.rport = rport or redis_cf[ 'port']
        self.rdb = rdb or redis_cf[ 'db']
        self.rusername = rusername or redis_cf[ 'username']
        self.rpassword = rpassword or redis_cf[ 'password']
        self.connect_timeout = connect_timeout or redis_cf['connect_timeout']

        self.enable_cooldown = enable_cooldown or cooldown_cf["enable"]
        self.cooldown_time = cooldown_time or cooldown_cf["time"]

        self.new_redis_client()
        self._load_resource_and_create_key()


    def new_redis_client(self):
        self.rclient = redis.StrictRedis(host=self.rhost, port=self.rport, username=self.rusername, password=self.rpassword,db=self.rdb, decode_responses=True)


    def _load_resource_and_create_key(self):
        self.key_name = "random_respool_main"    #set
        self.cooldown_pool_name = "random_cooldown_pool"  #set
        with open(self.resource_path, mode='r') as f:
            for line in f:
                member = {
                    "res": line.strip(),
                    "join_ts": int(time)
                    }
                self.rclient.sadd(self.key_name, str(member))
        logging.info("load {} objects to random pool {}".format(self.rclient.scard(self.key_name), self.key_name))


    def grab_one(self):
        self.new_redis_client()
        if self.enable_cooldown and self.cooldown_time:
            member = self.rclient.spop(self.key_name)
            new_member = eval(member)
            new_member["join_ts"] = int(time()) + self.cooldown_time
            self.rclient.sadd(self.cooldown_pool_name, str(new_member))
            res = eval(member)
        else:
            member = self.rclient.srandmember(self.key_name)
            res = eval(member)
        return res

    def refresh_cooldown_pool(self, interval=1):
        self.new_redis_client()
        while True:
            now = int(time())
            sleep(interval)
            for member in smembers(self.cooldown_pool_name):
                if now >= eval(member)["join_ts"]:
                    self.rclient.srem(self.cooldown_pool_name, member)
                    self.rclient.sadd(self.key_name, member)

