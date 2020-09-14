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

resource_path = "../resource.txt"


class PriorityPool(object):
    def __init__(self, resource_path=resource_path, rhost=None, rport=None, rusername=None, rpassword=None, rdb=None, connect_timeout=None):

        self.resource_path = resource_path
        self.rhost = rhost or redis_cf['host']
        self.rport = rport or redis_cf[ 'port']
        self.rdb = rdb or redis_cf[ 'db']
        self.rusername = rusername or redis_cf[ 'username']
        self.rpassword = rpassword or redis_cf[ 'password']
        self.connect_timeout = connect_timeout or redis_cf['connect_timeout']

        self.enable_discard = enable_discard or discard_cf['enable']
        self.discard_threshold = discard_threshold or discard_cf["threshold"]
        self._init_redis_client()
        self._load_resource_and_create_key()


    def _init_redis_client(self):
        connection_pool = redis.ConnectionPool(host=self.rhost, port=self.rport, username=self.rusername, password=self.rpassword,
            socket_connect_timeout=self.connect_timeout, db=self.rdb, decode_responses=True)
        self.rclient = redis.Redis(connection_pool=connection_pool)
        self.cmd1 = self.rclient.register_script(zpop)


    def _load_resource_and_create_key(self):
        self.key_name = "priority_respool_main"   # sortedset
        self.total_weight = 0
        with open(self.resource_path, mode="r") as f:
            for line in f:
                member = {
                        "res":line.strip(),
                        "score":100,
                        "join_ts": int(time()),
                        }
                if self.enable_discard:
                    member["discard"] = False
                self.rclient.zadd(self.key_name, 100, str(member))
                self.total_weight += 100
        logging.info("load {} objects to priority pool {}".format(self.rclient.scard(self.key_name), self.key_name))


    def grab_one(self):
        rand_num = random.uniform(-0.01, self.total_weight)
        iter_weight = 0
        for member in self.rclient.zscan_iter(self.key_name):
            iter_weight += eval(member[0])

    def dec_weight(self, res):
        old_score = self.rclient.zscore(self.key_name, res)
        if not old_score:
            return {"mas":"fail"} 
        self.rclient.zadd(self.key_name, old_score-1, res)
        self.total_weight -= 1
        return {"msg":"success"}
