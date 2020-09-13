import redis
import configparser
import os
import logging

from time import time
from ..utils import Exceptions


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt = '[%Y-%m-%d  %H:%M:%S]'
                    )

cf = configparser.ConfigParser()
cf.read("../config.ini")

redis_cf = dict(cf.items('redis')
pool_type_cf = dict(cf.items('pool-type'))
cooldown_cf = dict(cf.items('cooldown'))
discard_cf = dict(cf.items('discard'))

resource_path = "../resource.txt"


class pool(object):
    def __init__(self, resource_path=resource_path, rhost=None, rport=None, rusername=None, rpassword=None, rdb=None, connect_timeout=None, 
            pool_type=None, enable_cooldown=None, cooldown_time=None, enable_discard=None, discard_threshold=None):

        self.resource_path = resource_path
        self.rhost = rhost or redis_cf['host']
        self.rport = rport or redis_cf[ 'port']
        self.rdb = rdb or redis_cf[ 'db']
        self.rusername = rusername or redis_cf[ 'username']
        self.rpassword = rpassword or redis_cf[ 'password']
        self.connect_timeout = connect_timeout or redis_cf['connect_timeout']

        self.pool_type = pool_type or pool_type_cf['type']
        if self.pool_type not in ["random", "priority"]:
            raise Exceptions.ParamsError("pool_type must be random or priority")

        self.enable_cooldown = enable_cooldown or cooldown_cf["enable"]
        self.cooldown_time = cooldown_time or cooldown_cf["time"]

        self.enable_discard = enable_discard or discard_cf['enable']
        self.discard_threshold = discard_threshold or discard_cf["threshold"]
        self._init_redis_client()
        self.load_resource_and_create_key()

    def _init_redis_client(self):
        connection_pool = redis.ConnectionPool(host=self.rhost, port=self.rport, username=self.rusername, password=self.rpassword,
            socket_connect_timeout=self.connect_timeout, db=self.rdb, decode_responses=True)
        self.rclient = redis.Redis(connection_pool=connection_pool)

    def load_resource_and_create_key(self):
        if self.pool_type == "random":
            self.key_name = "random_respool_main"
            with open(self.resource_path, mode='r') as f:
                for line in f:
                    member = {
                        "res": line.strip(),
                        "join_ts": int(time)
                        }
                    if self.enable_cooldown:
                        member["cooldown_times"] = 0
                    if self.enable_discard:
                        member["discard"] = False
                    self.rclient.sadd(self.key_name, str(member))
            logging.info("load {} objects to random pool {}".format(self.rclient.scard(self.key_name), self.key_name))

        elif self.pool_type == "priority":
            self.key_name = "priority_respool_main"
            with open(self.resource_path, mode="r") as f:
                for line in f:
                    member = {
                            "res":line.strip(),
                            "join_ts": int(time()),
                            }
                    if self.enable_cooldown:
                        member["cooldown_times"] = 0
                    if self.enable_discard:
                        member["discard"] = False
                    self.rclient.zadd(self.key_name, 100, str(member))
            logging.info("load {} objects to priority pool {}".format(self.rclient.scard(self.key_name), self.key_name))


    def grab_one(self):
        pass 

    def discard(self):
        pass

    def rejoin(self):
        pass

    def grab_one(self):
        pass
        




