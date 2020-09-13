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

grab_one_lua = '''
local key = KEYS[]
local result = redis.call('ZRANGE', key, 0, 0)
local member = result[1]
if member then
    redis.call('ZREM', key, member)
    return member
else
    return nil
end
'''

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

        self._init_redis_client()
        self._load_resource_and_create_key()


    def _init_redis_client(self):
        connection_pool = redis.ConnectionPool(host=self.rhost, port=self.rport, username=self.rusername, password=self.rpassword,
            socket_connect_timeout=self.connect_timeout, db=self.rdb, decode_responses=True)
        self.rclient = redis.Redis(connection_pool=connection_pool)
        self.cmd1 = self.rclient.register_script(grab_one_lua)


    def _load_resource_and_create_key(self):
        self.key_name = "random_respool_main"
        with open(self.resource_path, mode='r') as f:
            for line in f:
                member = {
                    "res": line.strip(),
                    "join_ts": int(time)
                    }
                if self.enable_cooldown:
                    member["call_times"] = 0
                self.rclient.sadd(self.key_name, str(member))
        logging.info("load {} objects to random pool {}".format(self.rclient.scard(self.key_name), self.key_name))


    def grab_one(self):
        if self.enable_cooldown and self.cooldown_time:
            member = self.rclient.spop(self.key_name)
            new_member = eval(member)
            new_member["join_ts"] = int(time()) + self.cooldown_time
            new_member["call_times"] += 1
            self.rclient.sadd("random_cooldown_pool", str(new_member))
            res = eval(member)
        else:
            member = self.rclient.srandmember(self.key_name)
            res = eval(member)
        return res


class PriorityPool(object):
    def __init__(self, resource_path=resource_path, rhost=None, rport=None, rusername=None, rpassword=None, rdb=None, connect_timeout=None, 
                enable_cooldown=None, cooldown_time=None, enable_discard=None, discard_threshold=None):

        self.resource_path = resource_path
        self.rhost = rhost or redis_cf['host']
        self.rport = rport or redis_cf[ 'port']
        self.rdb = rdb or redis_cf[ 'db']
        self.rusername = rusername or redis_cf[ 'username']
        self.rpassword = rpassword or redis_cf[ 'password']
        self.connect_timeout = connect_timeout or redis_cf['connect_timeout']

        self.enable_cooldown = enable_cooldown or cooldown_cf["enable"]
        self.cooldown_time = cooldown_time or cooldown_cf["time"]

        self.enable_discard = enable_discard or discard_cf['enable']
        self.discard_threshold = discard_threshold or discard_cf["threshold"]
        self._init_redis_client()
        self._load_resource_and_create_key()

    def _init_redis_client(self):
        connection_pool = redis.ConnectionPool(host=self.rhost, port=self.rport, username=self.rusername, password=self.rpassword,
            socket_connect_timeout=self.connect_timeout, db=self.rdb, decode_responses=True)
        self.rclient = redis.Redis(connection_pool=connection_pool)
        self.cmd1 = self.rclient.register_script(grab_one_lua)

    def _load_resource_and_create_key(self):
        self.key_name = "priority_respool_main"
        with open(self.resource_path, mode="r") as f:
            for line in f:
                member = {
                        "res":line.strip(),
                        "score":100,
                        "join_ts": int(time()),
                        }
                if self.enable_cooldown:
                    member["call_times"] = 0
                if self.enable_discard:
                    member["discard"] = False
                self.rclient.zadd(self.key_name, 100, str(member))
        logging.info("load {} objects to priority pool {}".format(self.rclient.scard(self.key_name), self.key_name))


    def grab_one(self):
        if self.enable_cooldown and self.cooldown_time:
            pass
            

    def discard(self):
        pass

    def rejoin(self):
        pass


