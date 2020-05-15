import redis


class _DyBarrageRedisHandler:
    def __init__(self):
        print("连接 redis 中")
        self.__conn = redis.Redis(host='localhost', port=6379, db=0)
        self.__name = 'douyudanmu'
        print("连接 redis 成功")

    def __add(self, cmd):
      print("add command" + cmd)
      self.__conn.lpush(self.__name, cmd)

    def push(self, barrage):
        if barrage['txt']:
          for command in barrage['txt'].split('&&'):
            if command == "up":
              self.__add(command)
            elif command == "down":
              self.__add(command)
            elif command == "left":
              self.__add(command)
            elif command == "right":
              self.__add(command)
            elif command == "b":
              self.__add(command)
            elif command == "a":
              self.__add(command)

    def pop(self):
      return self.__conn.lpop(self.__name)

dy_barrage_redis_handler = _DyBarrageRedisHandler()
