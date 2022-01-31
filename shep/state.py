# local imports
from shep.error import (
        StateExists,
        StateInvalid,
        StateItemExists,
        StateItemNotFound,
        )


class State:

    def __init__(self, bits, logger=None):
        self.__bits = bits
        self.__limit = (1 << bits) - 1
        self.__c = 0
        self.NEW = 0

        self.__reverse = {0: self.NEW}
        self.__items = {self.NEW: []}
        self.__items_reverse = {}


    def __is_pure(self, v):
        c = 1
        for i in range(self.__bits):
            if c & v > 0:
                break
            c <<= 1
        return c == v


    def __check_name_valid(self, k):
        if not k.isalpha():
            raise ValueError('only alpha')

    def __check_name(self, k):
        self.__check_name_valid(k) 

        k = k.upper()
        try:
            getattr(self, k)
            raise StateExists(k)
        except AttributeError:
            pass
        return k


    def __check_valid(self, v):
        v = int(v)
        if self.__reverse.get(v):
            raise StateExists(v)
        return v


    def __check_value(self, v):
        v = self.__check_valid(v)
        if v > self.__limit:
            raise OverflowError(v)
        return v


    def __check_value_cursor(self, v):
        v = self.__check_valid(v)
        if v > 1 << self.__c:
            raise StateInvalid(v)
        return v


    def __set(self, k, v):
        setattr(self, k, v)
        self.__reverse[v] = k
        self.__c += 1


    def __check_item(self, item):
        if self.__items_reverse.get(item) != None:
            raise StateItemExists(item)


    def __add_state_list(self, state, item):
        if self.__items.get(state) == None:
            self.__items[state] = []
        self.__items[state].append(item)
        self.__items_reverse[item] = state


    def __state_list_index(self, item, state_list):
        idx = -1
        try:
            idx = state_list.index(item)
        except ValueError:
            pass

        if idx == -1:
            raise StateCorruptionError() # should have state int here as value

        return idx


    def add(self, k):
        v = 1 << self.__c
        k = self.__check_name(k)
        v = self.__check_value(v)
        self.__set(k, v)
        

    def alias(self, k, v):
        k = self.__check_name(k)
        v = self.__check_value_cursor(v)
        if self.__is_pure(v):
            raise ValueError('use add to add pure values')
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


    def name(self, v):
        if v == None:
            return self.NEW
        k = self.__reverse.get(v)
        if k == None:
            raise StateInvalid(v)
        return k


    def match(self, v, pure=False):
        alias = None
        if not pure:
            alias = self.__reverse.get(v)

        r = []
        c = 1
        for i in range(self.__bits):
            if v & c > 0:
                try:
                    k = self.__reverse[c]
                    r.append(k)
                except KeyError:
                    pass
            c <<= 1

        return (alias, r,)


    def put(self, item, state=None):
        if state == None:
            state = self.NEW
        elif self.__reverse.get(state) == None:
            raise StateInvalid(state)
        self.__check_item(item)
        self.__add_state_list(state, item)
                                

    def move(self, item, to_state):
        current_state = self.__items_reverse.get(item)
        if current_state == None:
            raise StateItemNotFound(item)

        new_state = self.__reverse.get(to_state)
        if new_state == None:
            raise StateInvalid(to_state)

        current_state_list = self.__items.get(current_state)
        if current_state_list == None:
            raise StateCorruptionError(current_state)

        idx = self.__state_list_index(item, current_state_list)

        new_state_list = self.__items.get(to_state)
        if current_state_list == None:
            raise StateCorruptionError(to_state)

        self.__add_state_list(to_state, item)
        current_state_list.pop(idx) 


    def purge(self, item):
        current_state = self.__items_reverse.get(item)
        if current_state == None:
            raise StateItemNotFound(item)
        del self.__items_reverse[item]

        current_state_list = self.__items.get(current_state)
        
        idx = self.__state_list_index(item, current_state_list)

        current_state_list.pop(idx) 


    def state(self, item):
        state = self.__items_reverse.get(item)
        if state == None:
            raise StateItemNotFound(item)
        return state
