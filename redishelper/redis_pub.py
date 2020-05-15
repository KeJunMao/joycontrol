from redis_helper import RedisHelper


obj = RedisHelper()
for i in range(5):
    obj.public("hello_%s" % i)
