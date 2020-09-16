import configparser


class Config():
    def load_config(self):
        cf = configparser.ConfigParser()
        cf.read("config.ini")
        redis_cf = dict(cf.items("redis"))
        self.REDIS_HOST = redis_cf["host"]
        self.REDIS_PORT = eval(redis_cf["port"])
        self.REDIS_DB = eval(redis_cf["db"])
        self.REDIS_USERNAME = eval(redis_cf["username"])
        self.REDIS_PASSWORD = eval(redis_cf["password"])
        self.CONNECT_TIMEOUT= eval(redis_cf["connect_timeout"])


        switch_cf = dict(cf.items("pool-switch"))
        self.ENABLE_RANDOM_POOL = eval(switch_cf["randompool"])
        self.ENABLE_PRIORITY_POOL = eval(switch_cf["prioritypool"])
        self.ENABLE_PROXY_POOL = eval(switch_cf["proxypool"])


        random_cf = dict(cf.items("RandomPool"))
        self.COOLDOWN_ENABLE = eval(random_cf["cooldown_enable"])
        self.COOLDOWN_TIME = eval(random_cf["cooldown_time"])
        self.REFRESH_INTERVAL = eval(random_cf["refresh_interval"])
        self.CLEAR_WHEN_BREAK_RANDOM = eval(random_cf["clear_when_break"])

        priority_cf = dict(cf.items("PriorityPool"))
        self.PRIORITY_INIT_SCORE = eval(priority_cf["init_score"])
        self.CLEAR_WHEN_BREAK_PRIORITY = eval(priority_cf["clear_when_break"])


        proxy_cf = dict(cf.items("ProxyPool"))
        self.PROXY_INIT_SCORE = eval(proxy_cf["init_score"])
        self.CAPACITY = eval(proxy_cf["capacity"])
        self.PROXY_SOURCE = proxy_cf["proxy_source"]
        self.AUTO_SUPPLEMENT = eval(proxy_cf["auto_supplement"])
        self.CLEAR_WHEN_BREAK_PROXY = eval(proxy_cf["clear_when_break"])

config = Config()
config.load_config()
