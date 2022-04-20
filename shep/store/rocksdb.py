# standard imports
import datetime
import os

# external imports
import rocksdb

# local imports
from .base import StoreFactory


class RocksDbStore:

    def __init__(self, path, db, binary=False):
        self.db = db
        self.__path = path
        self.__binary = binary


    def __to_key(self, k):
        return k.encode('utf-8')


    def __to_contents(self, v):
        if isinstance(v, bytes):
            return v
        return v.encode('utf-8')


    def __to_path(self, k):
        return '.'.join([self.__path, k])


    def __from_path(self, s):
        (left, right) = s.split('.', maxsplit=1)
        return right


    def __to_result(self, v):
        if self.__binary:
            return v
        return v.decode('utf-8')


    def put(self, k, contents=b''):
        if contents == None:
            contents = b''
        else:
            contents = self.__to_contents(contents)
        k = self.__to_path(k)
        k = self.__to_key(k)
        self.db.put(k, contents)


    def remove(self, k):
        k = self.__to_path(k)
        k = self.__to_key(k)
        self.db.delete(k)


    def get(self, k):
        k = self.__to_path(k)
        k = self.__to_key(k)
        v = self.db.get(k)
        return self.__to_result(v)

 
    def list(self):
        it = self.db.iteritems()
        kb_start = self.__to_key(self.__path)
        it.seek(kb_start)

        r = []
        l = len(self.__path)
        for (kb, v) in it:
            k = kb.decode('utf-8') 
            if len(k) < l or k[:l] != self.__path:
                break
            k = self.__from_path(k)
            v = self.db.get(kb)
            r.append((k, v,))

        return r


    def path(self):
        return None


    def replace(self, k, contents):
        if contents == None:
            contents = b''
        else:
            contents = self.__to_contents(contents)
        k = self.__to_path(k)
        k = self.__to_key(k)
        v = self.db.get(k)
        if v == None:
            raise FileNotFoundError(k)
        self.db.put(k, contents)


    def modified(self, k):
        k = self.__to_path(k)
        k = '_mod' + k
        v = self.db.get(k)
        return int(v)


    def register_modify(self, k):
        k = self.__to_path(k)
        k = '_mod' + k
        ts = datetime.datetime.utcnow().timestamp()
        self.db.set(k)


class RocksDbStoreFactory(StoreFactory):

    def __init__(self, path, binary=False):
        try:
            os.stat(path)
        except FileNotFoundError:
            os.makedirs(path)
        self.db = rocksdb.DB(path, rocksdb.Options(create_if_missing=True))
        self.__binary = binary


    def add(self, k):
        k = str(k)
        return RocksDbStore(k, self.db, binary=self.__binary)


    def close(self):
        self.db.close()


    def ls(self):
        it = self.db.iterkeys()
        it.seek_to_first()
        r = []
        for k in it:
            v = k.rsplit(b'.', maxsplit=1)
            if v != k:
                v = v[0].decode('utf-8')
                if v not in r:
                    r.append(v)
        return r
