from flask import Flask, g, request, jsonify
from poolhub.RandomPool import RandomPool
from poolhub.PriorityPool import PriorityPool
from utils import Exceptions
from config import config

import multiprocessing


app = Flask(__name__)

def get_pool_instance():
    pool_instances = {}
    if config.ENABLE_RANDOM_POOL:
        pool_instances["random"] =  RandomPool()

    if config.ENABLE_PRIORITY_POOL:
        pool_instances["priority"] = PriorityPool()
    return pool_instances


@app.route('/random')
def get_random_one():
    pool_instances = get_pool_instance()
    if "random" not in pool_instances:
        return jsonify({"msg":"random pool does not enable"})
    return jsonify(pool_instances["random"].grab_one())


@app.route('/priority')
def get_priority_one():
    pool_instances = get_pool_instance()
    if "priority" not in pool_instances:
        return jsonify({"msg":"priority pool does not enable"})
    return jsonify(pool_instances["priority"].grab_one())

@app.route('/dec_weight')
def dec_weight():
    pool_instances = get_pool_instance()
    if "priority" not in pool_instances:
        return jsonify({"msg":"priority pool does not enable"})
    res = request.args.get('res')
    return jsonify(pool_instances["priority"].dec_weight(res))

