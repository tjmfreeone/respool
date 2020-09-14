from flask import Flask, g, request, jsonify
import multiprocessing
from pool.RandomPool import RandomPool
from pool.PriorityPool import PriorityPool
from utils import Exceptions
import configparser


cf = configparser.ConfigParser()
cf.read("config.ini")

pool_type_cf = dict(cf.items('pool-type'))

if pool_type_cf["type"] not in ["random","priority"]:
    raise Exceptions.ParamsError("pool type must be random or priority")

app = Flask(__name__)

def init_pool():
    if pool_type_cf["type"] == "random":
        pool =  RandomPool()
    elif pool_type_cf["type"] == "priority":
        pool = PriorityPool()
    return pool


@app.route('/random')
def get_random_one():
    return jsonify(pool.grab_one())


@app.route('/priority')
def get_priority_one():
    return jsonify(pool.grab_one())

@app.route('/dec_weight')
def dec_weight():
    res = request.args.get('res')
    return jsonify(pool.dec_weight(res))


if __name__ == "__main__":
    pool = init_pool()
    app.run(host="0.0.0.0", port=5000, threaded=True)


