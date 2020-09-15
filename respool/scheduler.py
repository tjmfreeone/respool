import time
import multiprocessing
import logging
from config import config

from server import app, get_pool_instance
from poolhub.RandomPool import RandomPool
from poolhub.PriorityPool import PriorityPool


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt = '[%Y-%m-%d  %H:%M:%S]'
                    )

class Scheduler():
    def __init__(self):
        self.pool_instances = get_pool_instance()

    def run_server(self):
        app.run(host="0.0.0.0", port=5000, threaded=True)

    def refresh_random_cooldown_pool(self):
        self.pool_instances["random"].refresh_cooldown_pool()

    def run(self):
        try:
            logging.info("respool startup...")
            if not self.pool_instances:
                logging.info("No pool were enabled...")
                return
            for k in self.pool_instances.keys():
                logging.info("init a new {} pool".format(k))

            server_process = multiprocessing.Process(target=self.run_server)
            logging.info("server startup...")
            server_process.start()

            if "random" in self.pool_instances and config.COOLDOWN_ENABLE   :
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
            if config.CLEAR_WHEN_BREAK:
                self.pool_instances["random"].clear_pool()


