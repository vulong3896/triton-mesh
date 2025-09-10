from decouple import config
import redis

def init_redis():
    redis_url = config('REDIS_URL', default='redis://localhost:6379') + '/1'
    redis_pool = redis.ConnectionPool.from_url(redis_url)
    return redis.Redis(connection_pool=redis_pool)
