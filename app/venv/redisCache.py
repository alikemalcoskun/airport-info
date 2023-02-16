import redis
import redisConfig

r = redisConfig.redisConnect()

def getData(icao):
    return r.get(icao)

def setData(icao, data):
    r.set(icao, data)