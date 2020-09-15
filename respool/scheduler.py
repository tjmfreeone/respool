import time
import multiprocessing
import logging
import configparser

from server import app, get_pool_instance
from poolhub.RandomPool import RandomPool
from poolhub.PriorityPool import PriorityPool

cf = configparser.ConfigParser()
cf.read("./config.ini")


pool_type_cf = dict(cf.items('pool-type'))
cooldown_cf = dict(cf.items('cooldown'))
redis_cf = dict(cf.items("redis"))

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt = '[%Y-%m-%d  %H:%M:%S]'
                    )

class Scheduler():
    def __init__(self):
        self.pool = get_pool_instance()
    def run_server(self):
        app.run(host="0.0.0.0", port=5000, threaded=True)


    def refresh_random_cooldown_pool(self):
        self.pool.refresh_cooldown_pool()


    def run(self):
        try:
            logging.info("respool startup...")
            logging.info("init a new {} pool".format(pool_type_cf["type"]))

            server_process = multiprocessing.Process(target=self.run_server)
            logging.info("server startup...")
            server_process.start()

            if pool_type_cf["type"] == "random" and cooldown_cf["enable"]:
                refresh_process = multiprocessing.Process(target=self.refresh_random_cooldown_pool)
                logging.info("cooldown pool startup...")
                refresh_process.start()
            else:
                refresh_process = None

            server_process.join()
            if refresh_process:
                refresh_process.join()

        except KeyboardInterrupt:
            logging.info('keyboard interrupt')
            server_process.terminate()
            if refresh_process:
                refresh_process.terminate()

        finally:
            logging.info("respool process terminated")
            if redis_cf["clear_when_break"]:
                self.pool.clear_pool()


