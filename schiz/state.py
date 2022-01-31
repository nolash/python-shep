# standard imports
import enum
import logging

# local imports
from .error import StateExists

logg = logging.getLogger(__name__)


class State:

    def __init__(self, bits):
        self.__bits = bits
        self.__c = 0
        self.__reverse = {}

    def _persist(self):
        pass


    def add(self, name):
        if self.__c == self.__bits:
            raise OverflowError(self.__c + 1)
      
        v = 1 << self.__c

        k = name.upper()

        try:
            getattr(self, k)
            raise StateExists(k)
        except AttributeError:
            pass

        setattr(self, k, v)

        self.__c += 1
