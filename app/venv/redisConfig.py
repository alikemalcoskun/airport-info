import redis
import sys

def redisConnect():
    try:
        r = redis.Redis(host='localhost', port='6379', db='0')
        if r.ping() is True:
            return r

    except redis.ConnectionError:
        print("Redis connection error")
        sys.exit(1)
