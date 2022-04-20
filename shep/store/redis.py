# standard imports
import datetime

# external imports
import redis

# local imports
from .base import StoreFactory


class RedisStore:

    def __init__(self, path, redis, binary=False):
        self.redis = redis
        self.__path = path
        self.__binary = binary


    def __to_path(self, k):
        return '.'.join([self.__path, k])


    def __from_path(self, s):
        (left, right) = s.split(b'.', maxsplit=1)
        return right


    def __to_result(self, v):
        if self.__binary:
            return v
        return v.decode('utf-8')


    def put(self, k, contents=b''):
        if contents == None:
            contents = b''
        k = self.__to_path(k)
        self.redis.set(k, contents)


    def remove(self, k):
        k = self.__to_path(k)
        self.redis.delete(k)


    def get(self, k):
        k = self.__to_path(k)
        v = self.redis.get(k)
        return self.__to_result(v)

    
    def list(self):
        (cursor, matches) = self.redis.scan(match=self.__path + '.*')

        r = []
        for s in matches:
            k = self.__from_path(s)
            v = self.redis.get(k)
            r.append((k, v,))

        return r


    def path(self):
        return None


    def replace(self, k, contents):
        if contents == None:
            contents = b''
        k = self.__to_path(k)
        v = self.redis.get(k)
        if v == None:
            raise FileNotFoundError(k)
        self.redis.set(k, contents)


    def modified(self, k):
        k = self.__to_path(k)
        k = '_mod' + k
        v = self.redis.get(k)
        return int(v)


    def register_modify(self, k):
        k = self.__to_path(k)
        k = '_mod' + k
        ts = datetime.datetime.utcnow().timestamp()
        self.redis.set(k)


class RedisStoreFactory(StoreFactory):

    def __init__(self, host='localhost', port=6379, db=2, binary=False):
        self.redis = redis.Redis(host=host, port=port, db=db)
        self.__binary = binary


    def add(self, k):
        k = str(k)
        return RedisStore(k, self.redis, binary=self.__binary)


    def close(self):
        self.redis.close()


    def ls(self):
        r = []
        (c, ks) = self.redis.scan(match='*')
        for k in ks:
            v = k.rsplit(b'.', maxsplit=1)
            if v != k:
                v = v[0].decode('utf-8')
                if v not in r:
                    r.append(v)
        return r
