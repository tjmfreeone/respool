from flask import Flask, g, request, jsonify
from poolhub.RandomPool import RandomPool
from poolhub.PriorityPool import PriorityPool
from poolhub.ProxyPool import ProxyPool

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

    if config.ENABLE_PROXY_POOL:
        pool_instances["proxy"] = ProxyPool()
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


@app.route('/dec_proxy_weight')
def dec_proxy_weight():
    pool_instances = get_pool_instance()
    if "proxy" not in pool_instances:
        return jsonify({"msg":"proxy pool does not enable"})
    res = request.args.get('res')
    return jsonify(pool_instances["proxy"].dec_proxy_weight(res))


@app.route('/proxy')
def get_proxy_one():
    pool_instances = get_pool_instance()
    if "proxy" not in pool_instances:
        return jsonify({"msg":"proxy pool does not enable"})
    return jsonify(pool_instances["proxy"].grab_one())

@app.route('/pool_size')
def get_pool_size():
    pool_instances = get_pool_instance()
    pool_type = request.args.get('type')
    if pool_type not in pool_instances:
        return jsonify({"msg":"No such a pool in redis's keys."})
    return jsonify(pool_instances[pool_type].pool_size())

