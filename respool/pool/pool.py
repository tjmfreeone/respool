import redis
import configparser
import os
from ..utils import Exceptions

cf = configparser.ConfigParser()
cf.read("../config.ini")


redis_cf = dict(cf.items('redis')
pool_type_cf = dict(cf.items('pool-type'))
cooldown_cf = dict(cf.items('cooldown'))
discard_cf = dict(cf.items('discard'))


class pool(object):
    def __init__(self, rhost=None, rport=None, rusername=None, rpassword=None, rdb=None, connect_timeout=None, 
            pool_type=None, enable_cooldown=None, cooldown_time=None, enable_discard=None, discard_threshold=None):

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


    def _init_redis_client(self):
        connection_pool = redis.ConnectionPool(host=self.rhost, port=self.rport, username=self.rusername, password=self.rpassword,
            , socket_connect_timeout=self.connect_timeout, db=self.rdb, decode_responses=True)
        self.rclient = redis.Redis(connection_pool=connection_pool)

    def pop(self):
        pass

    def push(self):
        pass

    def grab_one(self):
        pass
        



