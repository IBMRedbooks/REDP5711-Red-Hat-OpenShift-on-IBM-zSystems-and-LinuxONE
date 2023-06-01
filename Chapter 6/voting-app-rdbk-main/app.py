from flask import Flask, render_template, request, make_response, g
from redis import Redis
import os
import platform
import socket
import random
import json

option_a = os.getenv('OPTION_A', "Moderna")
option_b = os.getenv('OPTION_B', "Pfizer")
hostname = socket.gethostname()
proc = platform.processor()

# may have to have env variable for Z

app = Flask(__name__)

def get_redis():
    if not hasattr(g, 'redis'):
        redishost = os.environ.get('REDIS_HOST', 'new-redis')
        redispassword = os.environ.get('REDIS_PASSWORD', 'admin')
        print ("Connecting to Redis using " + redishost)
        # g.redis = Redis(host=redishost, db=0, socket_timeout=5)
        # g.redis = Redis(host="10.130.3.187", port="6379", db=0, socket_timeout=5)
        g.redis = Redis(host=redishost, db=0, socket_timeout=5, password=redispassword)
        print (g.redis.ping())
    return g.redis


@app.route("/", methods=['POST','GET'])
def hello():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    vote = None

    if request.method == 'POST':
        redis = get_redis()
        vote = request.form['vote']
        data = json.dumps({'voter_id': voter_id, 'vote': vote})
        redis.rpush('votes', data)
        redis.ping
       

    resp = make_response(render_template(
        'index.html',
        option_a=option_a,
        option_b=option_b,
        hostname=hostname,
        vote=vote,
        proc=proc,
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
