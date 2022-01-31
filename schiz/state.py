# standard imports
import enum
import logging

# local imports
from schiz.error import (
        StateExists,
        StateInvalid,
        )

logg = logging.getLogger(__name__)


class State:

    def __init__(self, bits):
        self.__bits = bits
        self.__limit = (1 << bits) - 1
        self.__c = 0
        self.__reverse = {}

    def __store(self):
        pass

    
    def __is_pure(self, v):
        c = 1
        for i in range(self.__bits):
            if c & v > 0:
                break
            c <<= 1
        return c == v


    def __check_name(self, k):
        if not k.isalpha():
            raise ValueError('only alpha')
        k = k.upper()
        try:
            getattr(self, k)
            raise StateExists(k)
        except AttributeError:
            pass
        return k


    def __check_cover(self, v):
        z = 0
        c = 1
        for i in range(self.__bits):
            if c & v > 0:
                if self.__reverse.get(c) == None:
                    raise StateInvalid(v)
            c <<= 1
        return c == v


    def __check_value(self, v):
        v = int(v)
        if self.__reverse.get(v):
            raise StateValueExists(v)
        if v > self.__limit:
            raise OverflowError(v)
        return v


    def __check(self, k, v):
        k = self.__check_name(k)
        v = self.__check_value(v)
        return (k, v,)


    def __set(self, k, v):
        setattr(self, k, v)
        self.__reverse[v] = k
        self.__c += 1


    def add(self, k):
        v = 1 << self.__c
        (k, v) = self.__check(k, v)
        self.__set(k, v)
        

    def alias(self, k, v):
        (k, v) = self.__check(k, v)
        if self.__is_pure(v):
            raise ValueError('use add to add pure values')
        self.__check_cover(v) 
        self.__set(k, v)


    def all(self):
        l = []
        for k in dir(self):
            if k[0] == '_':
                continue
            if k.upper() != k:
                continue
            l.append(k)
        l.sort()
        return l
